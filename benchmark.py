import time
import requests
import concurrent.futures
import json

URL = "http://localhost:5000/chat"
PAYLOAD = {
    "messages": [{"role": "user", "content": "写一段Python快速排序代码，并解释时间复杂度"}],
    "temperature": 0.7,
    "max_tokens": 256
}

def single_request(idx):
    start = time.time()
    try:
        r = requests.post(URL, json=PAYLOAD, timeout=60)
        latency = time.time() - start
        if r.status_code == 200:
            data = r.json()
            return {
                "idx": idx,
                "latency": latency,
                "status": r.status_code,
                "tokens": data.get("completion_tokens", 0),
                "error": None
            }
        else:
            return {"idx": idx, "latency": latency, "status": r.status_code, "tokens": 0, "error": r.text}
    except Exception as e:
        return {"idx": idx, "latency": time.time() - start, "status": 0, "tokens": 0, "error": str(e)}

def run_benchmark(concurrency, total=20):
    print(f"\n{'='*50}")
    print(f"并发数: {concurrency}, 总请求: {total}")
    print(f"{'='*50}")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as ex:
        futures = [ex.submit(single_request, i) for i in range(total)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    # 统计
    latencies = [r["latency"] for r in results if r["status"] == 200]
    tokens = [r["tokens"] for r in results if r["status"] == 200]
    errors = [r for r in results if r["status"] != 200]
    
    if latencies:
        print(f"成功: {len(latencies)}/{total}")
        print(f"平均延迟: {sum(latencies)/len(latencies):.3f}s")
        print(f"最大延迟: {max(latencies):.3f}s")
        print(f"最小延迟: {min(latencies):.3f}s")
        print(f"总生成token: {sum(tokens)}")
        print(f"平均token/请求: {sum(tokens)/len(tokens):.1f}")
    if errors:
        print(f"失败: {len(errors)}")
        for e in errors[:3]:
            print(f"  错误: {e['error'][:100]}")
    
    return results

if __name__ == '__main__':
    # 先预热1次
    print("预热中...")
    requests.post(URL, json=PAYLOAD)
    time.sleep(1)
    
    # 压测
    for c in [1, 2, 4]:
        run_benchmark(c, total=20)
        time.sleep(2)
