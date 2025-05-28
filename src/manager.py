import logging
from collections import defaultdict
from typing import Literal, Any

from steampy.client import SteamClient
from steampy.models import Currency, GameOptions


from src.db.models import BuyOrder
from src.db.utils import get_ids_from_db, delete_ids_from_db
from src.utils import GAME_NAME_BY_APPID, parse_price_value

MY_LISTINGS = dict[
    Literal['buy_orders', 'sell_listings'],
    dict[str, dict[Literal['order_id', 'quantity', 'price', 'item_name', 'icon_url', 'game_name'], Any]]
]
GAME_NAME = ITEM_NAME = str


class BuyOrderManager:

    def __init__(self, steam_client: SteamClient):
        self._steam_client = steam_client
        self._buy_orders: defaultdict[GAME_NAME, dict[ITEM_NAME, BuyOrder]] = defaultdict(dict)
        self._steam_id = self._steam_client.get_steam_id()
        self._log = logging.getLogger(f'{self.__class__.__name__}({self._steam_id})')

    def cancel_order(self, order: BuyOrder):
        """
        Отменить ордер.
        Вся информация автоматически удаляется из БД.
        """
        self._steam_client.market.cancel_buy_order(order.id)
        self._log.info(f'Снят ордер {order.id} на предмет "{order.item_name}" по цене {order.price}')
        order.delete_from_db()
        del self._buy_orders[order.game_name][order.item_name]

    def create_order(
        self,
        market_name: str,
        price_single_item: str,
        quantity: int,
        game: GameOptions,
        currency: Currency = Currency.USD,
    ) -> BuyOrder:
        """
        Создать ордер.
        Вся информация автоматически сохраняется в БД.
        :param price_single_item: Целое число
        """
        response = self._steam_client.market.create_buy_order(
            market_name=market_name,
            price_single_item=price_single_item,
            quantity=quantity,
            game=game,
            currency=currency
        )
        order = BuyOrder(
            id=response['buy_orderid'],
            steam_id=str(self._steam_id),
            quantity=quantity,
            price=round(int(price_single_item) / 100, 2),
            item_name=market_name,
            game_name=GAME_NAME_BY_APPID[game.app_id]
        )
        self._buy_orders[GAME_NAME_BY_APPID[game.app_id]][market_name] = order
        self._log.info(f'Создан ордер {order.id} на предмет "{order.item_name}" по цене {order.price}')
        order.save_to_db()
        return order

    def _refresh_local_orders(self, response: MY_LISTINGS, existing_orders_id: set[str]) -> set[str]:
        """
        Обновить локальные ордера.
        Сохраняет в БД, если нет записи с таким id
        :return: Множество id
        """
        self._buy_orders.clear()
        new_orders_ids = set()
        for info in response['buy_orders'].values():
            order = BuyOrder(id=str(info['order_id']),
                             steam_id=str(self._steam_id),
                             quantity=int(info['quantity']),
                             price=parse_price_value(info['price']),
                             item_name=info['item_name'],
                             game_name=info['game_name'])
            self._buy_orders[info['game_name']][info['item_name']] = order
            new_orders_ids.add(order.id)
            if order.id not in existing_orders_id:
                order.save_to_db()
        return new_orders_ids

    def refresh_orders(self):
        """Обновить информацию о выставленных ордерах на покупку.
        Также обновляется информация в БД"""
        response: MY_LISTINGS = self._steam_client.market.get_my_market_listings()
        existing_orders_ids = get_ids_from_db()
        new_orders_ids = self._refresh_local_orders(response, existing_orders_ids)
        self._log.debug(f'Получено {len(new_orders_ids)} активных ордеров на покупку')
        ids_to_delete = existing_orders_ids.difference(new_orders_ids)
        if ids_to_delete:
            delete_ids_from_db(ids_to_delete)
            self._log.debug(f'Удалено {len(ids_to_delete)} неактуальных ордеров на покупку из БД')

    def check_order(self, order: BuyOrder, refresh_orders: bool = True) -> bool:
        """
        Возвращает True, если ордер выставлен.
        :param refresh_orders: Если выставлен в True, обновляет информацию об ордерах перед проверкой.
        """
        if refresh_orders:
            self.refresh_orders()
        local_order = self._buy_orders[order.game_name].get(order.item_name)
        if local_order is None:
            return False
        return local_order.id == order.id

    def find_order(self, game_name: GAME_NAME, item_name: str, refresh_orders: bool = True) -> BuyOrder | None:
        """
        Возвращает ордер на предмет, если он существует.
        :param game_name: Имя игры
        :param item_name: Имя предмета
        :param refresh_orders: Если выставлен в True, обновляет информацию об ордерах перед проверкой.
        """
        if refresh_orders:
            self.refresh_orders()
        return self._buy_orders[game_name].get(item_name)
