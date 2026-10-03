const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export type Employee = { id: number; name: string };

export async function listEmployees(): Promise<Employee[]> {
  const res = await fetch(`${API_URL}/employees`);
  if (!res.ok) throw new Error(`GET /employees failed: ${res.status}`);
  return res.json();
}

export async function listSubordinates(leaderId: number): Promise<Employee[]> {
  const res = await fetch(`${API_URL}/subordinates`, {
    headers: { "X-Leader-Id": String(leaderId) },
  });
  if (!res.ok) throw new Error(`GET /subordinates failed: ${res.status}`);
  return res.json();
}