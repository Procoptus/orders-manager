# orders-manager

Перед запуском нужно создать `.env` в корневой директории проекта со следующими ключами:
```
DB_URL="mysql+pymysql://<username>:<password>@<host>/<dbname>[?<options>]"
```

Взаимодействовать с `BuyOrderManager`.

Если только развернули проект, и в библиотеке steampy, до сих пор не пофиксили финальный запрос в `/jwt/finalizelogin`, 
то используем фикс из https://github.com/bukson/steampy/issues/435
