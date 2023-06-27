from datetime import datetime
from elasticsearch import Elasticsearch, exceptions
from elasticsearch.exceptions import RequestError


# Elasticsearch connection details
es_host = 'localhost'
es_port = 9200
es_username = 'Username'  # If authentication is enabled
es_password = 'Password'  # If authentication is enabled

# Elasticsearch client instance
es = Elasticsearch(
    hosts=[{'host': es_host, 'port': es_port}],
    http_auth=(es_username, es_password)
)

# Define the ILM policy
ilm_policy = {
    "policy": {
        "phases": {
            "hot": {
                "actions": {
                    "rollover": {
                        "max_size": "50GB",
                        "max_age": "30d"
                    }
                }
            },
            "warm": {
                "actions": {
                    "forcemerge": {
                        "max_num_segments": 1
                    },
                    "shrink": {
                        "number_of_shards": 1
                    }
                },
                "min_age": "30d"
            },
            "cold": {
                "actions": {
                    "freeze": {}
                },
                "min_age": "60d"
            },
            "compress": {
                "actions": {
                    "readonly": {},
                    "forcemerge": {
                        "max_num_sements": 1
                    },
                    "shrink": {
                        "number_of_shards": 1
                    },
                    "freeze": {},
                    "index": {
                        "lifecycle_name": "compress",
                        "compression": "true"
                    }
                }
            },   
            "delete": {
                "min_age": "90d",
                "actions": {
                    "delete": {}
                }
            }
        }
    }
}

# Create the ILM policy for logs

policy_name = 'logs_policy'
try:
    es.index_lifecycle.create_lifecycle_policy(policy_name, ilm_policy)
    print(f"ILM policy '{policy_name}' created successfully.")
except exceptions.RequestError as e:
    print(f"Failed to create ILM policy. Error: {e}")

# Associate the ILM policy with an index pattern
index_pattern = 'logs-*'
try:
    es.index_lifecycle.put_lifecycle_policy(index_pattern, policy_name)
    print(f"ILM policy '{policy_name}' associated with index pattern '{index_pattern}'.")
except exceptions.RequestError as e:
    print(f"Failed to associate ILM policy with index pattern. Error: {e}")
    
# Attach ILM policy to the index
es.indices.put_settings(
    index=index_name,
    body={
        "settings": {
            "index": {
                "lifecycle": {
                    "name": ilm_policy_name,
                    "rollover_alias": index_name
                }
            }
        }
    }
)