from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
import time

pushgateway_address = '127.0.0.1:9091'
lnames = ['system', 'model', 'subquery']

registry = CollectorRegistry()

total_duration = Gauge('total_duration', 'time spent generating the response', labelnames=lnames, registry=registry)
prompt_eval_duration = Gauge('prompt_eval_duration', 'time spent in nanoseconds evaluating the prompt', labelnames=lnames, registry=registry)
prompt_eval_count = Gauge('prompt_eval_count', 'number of tokens in the prompt', labelnames=lnames, registry=registry)
eval_count = Gauge('eval_count', 'number of tokens in the response', labelnames=lnames, registry=registry)
correct_answer = Gauge('correct_answer', 'count_correct_answer', labelnames=lnames[:2], registry=registry)
total_answer = Gauge('total_answer', 'count_total_answer', labelnames=lnames[:2], registry=registry)


def send(data: dict):
    system_llm = data.get('system')
    model_name = data.get('model')

    resp_metrics = data.get('response')
    for subquery_count, m in enumerate(resp_metrics):
        total_duration.labels(system=system_llm, model=model_name, subquery=subquery_count).set(m.get('generation_info_total_duration'))
        prompt_eval_duration.labels(system=system_llm, model=model_name,subquery=subquery_count).set(m.get('generation_info_prompt_eval_duration'))
        prompt_eval_count.labels(system=system_llm, model=model_name, subquery=subquery_count).set(m.get('generation_info_prompt_eval_count'))
        eval_count.labels(system=system_llm, model=model_name, subquery=subquery_count).set(m.get('generation_info_eval_count'))

    if data.get('correct_answers') is not None:
        correct_answer.labels(system=system_llm, model=model_name).set(data.get('correct_answers'))
    total_answer.labels(system=system_llm, model=model_name).set(data.get('total_answers'))

    push_to_gateway(pushgateway_address, 'llm', registry)
