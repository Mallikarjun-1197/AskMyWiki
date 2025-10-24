    "vectorSearch":{
        "algorithmConfigurations":[
            {
                "name":"vector-algorithm",
                "kind":"hnsw",
                "parameters":{
                    "m":"4",
                    "efConstruction":400,
                    "efSearch":500,
                    "metric":"cosine"
                }
            }
        ]
    }

two types of algos used   : hnsw or exhaustiveKnn .. These are Approximate neighbours ANN algos used to organize vectors
during indexing

m represents bi-directional link count default 4 10, low value means less noise in result
efConstr = no of neighbours used during indexing
efSearch = no of neighbours used during searching.
metric : cosine for AzureOpenAI, depending on model it can be dotProduct, euclidiean, hamming..

Make sure the name of the index name you choose is in lowercase and do not include and _ or - :)

https://learn.microsoft.com/en-us/azure/search/search-api-migration
https://learn.microsoft.com/en-us/rest/api/searchservice/documents/?view=rest-searchservice-2025-09-01&tabs=HTTP