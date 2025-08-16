--- Create configuration table
DROP TABLE IF EXISTS agents_grocery_config;
CREATE TABLE IF NOT EXISTS agents_grocery_config (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) UNIQUE NOT NULL,
    value JSONB NOT NULL,
    description TEXT,
    env TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (key, env)
);

--- Insert or Update configurations
INSERT INTO agents_grocery_config (key, value, description, env) VALUES
(
  'agents',
  '{
    "qa_agent": {
      "inference": {
        "llm": {
          "provider": "gpt_4o_mini"
        },
        "embeddings": {
          "provider": "local"
        }
      }
    }
  }',
  'Service configurations',
  'dev'
)
ON CONFLICT (key, env) DO UPDATE SET
  value = EXCLUDED.value,
  description = EXCLUDED.description,
  updated_at = CURRENT_TIMESTAMP;

INSERT INTO agents_grocery_config (key, value, description, env) VALUES
(
  'inference',
  '{
    "llm": {
      "providers": {
        "gpt_4o_mini": {
          "model_config": {
            "model": "gpt-4o-mini",
            "temperature": 0,
            "top_p": 1.0,
            "max_tokens": 8192,
            "n": 1
          },
          "invoke_config": {
            "max_concurrency": 16
          }
        },
        "gpt_41_mini": {
          "model_config": {
            "model": "gpt-4.1-mini",
            "temperature": 0,
            "top_p": 1.0,
            "max_tokens": 8192,
            "n": 1
          },
          "invoke_config": {
            "max_concurrency": 16
          }
        },
        "tpu_naver_14b": {
          "model_config": {
            "openai_api_key": "empty",
            "openai_api_base": "http://173.255.121.245:8000/v1",
            "model": "/workspace/naver-14b-local/",
            "temperature": 0.5,
            "max_tokens": 8192,
            "stop": [
              "<|im_end|><|endofturn|>",
              "<|im_end|><|stop|>"
            ],
            "n": 1,
            "extra_body": {
              "skip_special_tokens": false,
              "repetition_penalty": 1.05,
              "top_k": -1,
              "chat_template_kwargs": {
                "skip_reasoning": true
              }
            }
          },
          "invoke_config": {
            "max_concurrency": 16
          }
        }
      },
      "cache": {
        "index": "agents_grocery_llm_cache"
      }
    },
    "embeddings": {
      "provider": "local",
      "providers": {
        "local": {
          "model_config": {
            "openai_api_key": "empty",
            "openai_api_base": "http://192.168.0.191:58001/v1",
            "model": "dragonkue/snowflake-arctic-embed-l-v2.0-ko",
            "tiktoken_enabled": false
          },
          "dimensions": 1024
        }
      },
      "cache": {
        "index": "agents_grocery_embeddings_cache"
      }
    }
  }',
  'Inference configurations',
  'dev'
)
ON CONFLICT (key, env) DO UPDATE SET
  value = EXCLUDED.value,
  description = EXCLUDED.description,
  updated_at = CURRENT_TIMESTAMP;

INSERT INTO agents_grocery_config (key, value, description, env) VALUES
(
  'elasticsearch',
  '{
    "dataset": {
      "naver_news": {
        "index": {
          "source": {
            "name": "naver_news_source",
            "pkey": ["url", "dataset_version", "content"],
            "version": "v0.0.2"
          },
          "transform": {
            "name": "naver_news_transform",
            "pkey": ["source_id", "llm_model", "embeddings_model", "dataset_version"],
            "version": "v0.0.3"
          }
        }
      },
      "aitimes": {
        "index": {
          "source": {
            "name": "aitimes_source",
            "pkey": ["url", "dataset_version", "content"],
            "version": "v0.0.2"
          },
          "transform": {
            "name": "aitimes_transform",
            "pkey": ["source_id", "llm_model", "embeddings_model", "dataset_version"],
            "version": "v0.0.3"
          }
        }
      }
    }
  }',
  'Elasticsearch configurations',
  'dev'
)
ON CONFLICT (key, env) DO UPDATE SET
  value = EXCLUDED.value,
  description = EXCLUDED.description,
  updated_at = CURRENT_TIMESTAMP;

INSERT INTO agents_grocery_config (key, value, description, env) VALUES
(
  'logstash',
  '{
    "host": "alchemine.iptime.org",
    "general_log_port": 5962,
    "chat_history_log_port": 5963,
    "api_log_port": 5964
  }',
  'Logstash configurations',
  'dev'
)
ON CONFLICT (key, env) DO UPDATE SET
  value = EXCLUDED.value,
  description = EXCLUDED.description,
  updated_at = CURRENT_TIMESTAMP;