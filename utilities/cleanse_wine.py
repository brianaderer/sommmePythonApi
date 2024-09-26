import singleton as singleton
import time


class CleanseWine:
    producerFilter = None
    cuveeFilter = None
    vintageFilter = None
    wine = None
    producer = None
    cuvee = None
    vintage = None
    result = None
    wine_id = None
    result_length = None
    owner_id = None

    def __init__(self):
        self.owner_filter = None
        self.wine_filter = None
        self.user_wine = None
        self.returned_docs = None
        self.s = singleton.Singleton()
        self.Filter = self.s.Firebase.FieldFilter
        self.bev_ref = self.s.Firebase.db.collection('beverages')
        self.variant_ref = self.s.Firebase.db.collection('variants')
        self.variants = []

    def reset(self):
        self.producerFilter = None
        self.owner_id = None
        self.cuveeFilter = None
        self.vintageFilter = None
        self.wine = None
        self.user_wine = None
        self.producer = None
        self.cuvee = None
        self.vintage = None
        self.wine_id = None
        self.returned_docs = []

    def handle_wine_cleanse(self, wine, owner_id):
        self.reset()
        self.owner_id = owner_id
        self.user_wine = wine
        self.find_wine_by_attrs()
        self.set_up_filters()
        start_time = time.time()  # Start the timer
        self.execute_query()  # Execute the query
        end_time = time.time()  # End the timer
        elapsed_time = end_time - start_time  # Calculate the elapsed time
        print(f"Query executed in {elapsed_time:.2f} seconds")  # Print the time in seconds.00 format
        if len(self.returned_docs) == 1:
            self.wine = self.returned_docs[0]
            self.wine_id = list(self.wine.keys())[0]
            self.compare_wine()
        elif len(self.returned_docs) == 0:
            self.create_wine()

    def compare_wine(self):
        self.variants=[]
        self.set_up_wine_filters()
        returned_wine = self.wine[list(self.wine.keys())[0]]
        returned_wine_without_owner = {k: v for k, v in returned_wine.items() if k not in ['owners']}
        user_wine_without_owner = {k: v for k, v in self.user_wine.items() if k not in ['owners']}
        user_keys = list(user_wine_without_owner.keys())
        variant = {}
        for key in user_keys:
            if key not in returned_wine_without_owner or user_wine_without_owner[key] != returned_wine_without_owner[key]:
                variant[key] = user_wine_without_owner[key]
        docs = (
            self.variant_ref
            .where(filter=self.wine_filter)
            .where(filter=self.owner_filter)
            .stream()
        )
        for doc in docs:
            self.variants.append({doc.ref_id: doc.to_dict()})
        if len(list(variant.keys())):
            if not len(self.variants):
                doc_ref = self.variant_ref.add({
                    'ownerId': self.owner_id,
                    'wineId': self.wine_id,
                    'data': variant,
                    'reviewed': False,
                })
            else:
                var_data = self.variants[0]
                var_data_key = list(var_data.keys())[0]
                var_data_value = var_data[var_data_key]
                if var_data_value['data'] != variant:
                    var_data[var_data_key]['data'] = variant
                    doc_ref = self.variant_ref.document(var_data_key)
                    doc_ref.update(var_data)
        elif len(self.variants):
            var_data = self.variants[0]
            var_data_key = list(var_data.keys())[0]
            doc_ref = self.variant_ref.document(var_data_key)
            doc_ref.delete()


    def find_wine_by_attrs(self):
        self.producer = self.user_wine['producers'][0]
        self.cuvee = self.user_wine['cuvees'][0]
        self.vintage = self.user_wine['vintage'][0]

    def create_wine(self):
        doc_ref = self.bev_ref.add(self.user_wine)
        self.wine = {doc_ref[1].ref_id: self.user_wine}
        self.wine_id = doc_ref[1].ref_id

    def set_up_wine_filters(self):
        self.wine_filter = self.s.Firebase.FieldFilter('wineId', '==', self.wine_id)
        self.owner_filter = self.s.Firebase.FieldFilter('ownerId', '==', self.owner_id)

    def check_for_other_vintages(self):
        docs = (self.bev_ref
                .where(filter=self.producerFilter)
                .where(filter=self.cuveeFilter)
                .stream())

    def set_up_filters(self):
        self.producerFilter = self.Filter('producers', '==', [self.producer])
        self.cuveeFilter = self.Filter('cuvees', '==', [self.cuvee])
        self.vintageFilter = self.Filter('vintage', '==', [self.vintage])

    def parse_query_result(self):
        print('found data')
        for doc in self.result:
            print(f"ID: {doc.id}")

    def execute_query(self):
        docs = (self.bev_ref
                .where(filter=self.producerFilter)
                .where(filter=self.cuveeFilter)
                .where(filter=self.vintageFilter)
                .stream())
        for doc in docs:
            self.returned_docs.append({doc.id: doc.to_dict()})
