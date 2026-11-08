"""Chạy giả thuyết LAB080 bằng khung Inspect (UK AISI) khi cần chạy lớn nhiều model.

  pip install inspect_ai
  inspect eval inspect_thoi_quen.py -T de=../../../data/de-essays-150.jsonl -T hyp=../gia-thuyet/thu-vien-en.json \
      --model openrouter/openai/gpt-4o-mini,openrouter/x-ai/grok-4-fast --epochs 3 --log-dir logs
  python inspect_thoi_quen.py logs data/inspect.jsonl   # đổi nhật ký thành jsonl, rồi tqa.py test như thường

Inspect lo phần gọi model, song song, chạy lại, nhật ký, giao diện xem (inspect view); điểm số mỗi bài
là thước đo của tqa.do cho từng giả thuyết. So sánh giữa model, CI, Holm vẫn do tqa.py test làm.
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import tqa
from inspect_ai import Task, task
from inspect_ai.dataset import Sample, json_dataset
from inspect_ai.scorer import Score, Target, mean, scorer, stderr
from inspect_ai.solver import TaskState, generate, system_message


@scorer(metrics={'*': [mean(), stderr()]})
def thoi_quen(hyp: str):
    hs = json.loads(Path(hyp).read_text(encoding='utf-8'))

    async def score(state: TaskState, target: Target):
        t = state.output.completion
        return Score(value={h['id']: tqa.do(t, h['metric']) for h in hs}, answer=t[:200])
    return score


@task
def thoi_quen_ai(de: str, hyp: str, system: str = 'You are a helpful assistant.'):
    ds = json_dataset(de, lambda r: Sample(input=r['prompt'], id=r['id']))
    return Task(dataset=ds, solver=[system_message(system), generate()], scorer=thoi_quen(hyp))


if __name__ == '__main__':  # đổi nhật ký Inspect → jsonl của tqa
    from inspect_ai.log import list_eval_logs, read_eval_log
    with open(sys.argv[2], 'a', encoding='utf-8') as f:
        for info in list_eval_logs(sys.argv[1]):
            log = read_eval_log(info)
            for s in log.samples or []:
                f.write(json.dumps({'model': log.eval.model, 'prompt_id': s.id, 'sample': s.epoch - 1,
                                    'output': s.output.completion}, ensure_ascii=False) + '\n')
