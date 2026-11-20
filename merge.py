from pymongo import MongoClient
from pymongo.database import Database


def show(db: Database):
    collections = db.list_collection_names()
    print(f'Collections: {collections}')

    ug = db.get_collection('user_group')
    mug = db.get_collection('mongo_user_group')

    print(f'mongo_user_group: {mug.count_documents({})} docs')
    print(f'user_group: {ug.count_documents({})} docs')

    ug_ids = set(ug.distinct('_id'))
    mug_ids = set(mug.distinct('_id'))
    print(f'Ids in mongo_user_group but not in user_group: {mug_ids - ug_ids}')


def merge(db: Database):
    new_groups = db.get_collection('mongo_user_group')
    result = new_groups.aggregate(
        [
            {'$match': {}},
            {
                '$merge': {
                    'into': 'user_group',
                    'on': '_id',
                    'whenMatched': 'keepExisting',
                    'whenNotMatched': 'insert',
                }
            },
        ]
    )


def remove(db: Database):
    db.get_collection('mongo_user_group').drop()


if __name__ == '__main__':
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument('--host', required=True, help='MongoDB host (common: localhost)')
    ap.add_argument(
        '--port', type=int, default=27017, help='MongoDB port (default: 27017)'
    )
    ap.add_argument(
        '--db-name', required=True, help='MongoDB Database name (common: nomad_v1)'
    )
    ap.add_argument('--username', help='MongoDB username')
    ap.add_argument('--password', help='MongoDB password')
    ap.add_argument('--action', required=True, help='Action to perform',
                    choices=['show', 'merge', 'remove'], default='show')

    args = ap.parse_args()

    client = MongoClient(
        host=args.host, port=args.port, username=args.username, password=args.password
    )
    db = client.get_database(args.db_name)
    if args.action == 'show':
        show(db)
    elif args.action == 'merge':
        merge(db)
    elif args.action == 'remove':
        remove(db)

    client.close()
