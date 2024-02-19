from prisma import Prisma
import asyncio


class DB:
    async def get_last_value_product():
        db = Prisma()
        await db.connect()
        get_lastd_id_value = await db.product.find_many(
            order=[{
                'id': 'desc'
            }]
        )

        await db.disconnect()
        if not get_lastd_id_value:
            return 0

        return get_lastd_id_value[0].id

    async def create_product(product_data):
        if product_data:
            db = Prisma()
            await db.connect()
            await db.product.create_many(
                data=product_data,
                skip_duplicates=True
            )
            await db.disconnect()

    async def create_historic_product(historic_product):
        if historic_product:
            db = Prisma()
            await db.connect()
            await db.product_history.create_many(
                data=historic_product,
            )
            await db.disconnect()

    async def get_product(product_id=int):
        db = Prisma()
        await db.connect()
        try:
            product = await db.product.find_unique(
                where={
                    "id": product_id,
                },
                include={
                    'History': True
                },
            )

            historic = await db.product_history.find_many(
                where={
                    "productId": product_id
                }
            )

            his = list()
            for h in historic:
                value = h.dict()
                k = {
                    "Data": value["dia"],
                    "Preço": value["preco"],
                    "A vista": value["avista"],
                    "Parcelado": value["parcelado"]
                }
                his.append(k)

            dic = {
                "Nome": product.Nome,
                "Link": product.link,
                "Historico": his
            }

            await db.disconnect()
            return dic
        except:
            await db.disconnect()
            return "Produto não encontrado"
