const TOKEN = 'dev-token';

export async function emitBusTask(payload: any) {
  await fetch('http://127.0.0.1:8765/agents', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${TOKEN}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });
}
