def postgres_upsert(pk_name):
    def do(table, conn, keys, data_iter):
        from sqlalchemy.dialects.postgresql import insert

        data = [dict(zip(keys, row)) for row in data_iter]

        insert_statement = insert(table.table).values(data)
        upsert_statement = insert_statement.on_conflict_do_update(
            constraint=pk_name,
            set_={c.key: c for c in insert_statement.excluded},
        )
        conn.execute(upsert_statement)
    return do