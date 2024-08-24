import singleton
class ProducerType:

    def __init__(self, producer, key=0):
        self.s = singleton.Singleton()
        producer_key = self.get_key(producer)
        producer_val = producer[producer_key]
        producer_dict = {0: {'owners': producer_val['owners'], 'cuvees': producer_val['cuvees'], 'value': producer_val['value'],
                             'db_id': producer_key}}