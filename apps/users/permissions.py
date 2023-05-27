from rest_framework_api_key.permissions import BaseHasAPIKey
from .models import ChainVetAPIKey

class HasChainVetAPIKey(BaseHasAPIKey):
    model = ChainVetAPIKey