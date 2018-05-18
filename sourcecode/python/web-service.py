import hug


@hug.get(examples='query=select')
@hug.local()
def generate_data(query: hug.types.text):
    """Does nothing right now"""
    response = 'No data found'
    return {
        'message': 'need to provide message here',
        'query': '{0}'.format(query),
        'response': response}
