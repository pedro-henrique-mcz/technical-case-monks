const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export type Employee = { id: number; name: string };

export type Highlight = { leader_name: string; week_start: string; final_score: number };

export type Subordinate = Employee & { position_name: string; highlight: Highlight | null };

export type Question = { id: number; label: string; weight: number };

export type Answer = { question_id: number; label: string; weight: number; score: number };

export type Evaluation = {
  id: number;
  leader_id: number;
  leader_name: string;
  week_start: string; // "YYYY-MM-DD", the Monday of the week
  final_score: number;
  answers: Answer[];
};

export type AnswerInput = { question_id: number; score: number };

// Carries the HTTP status, so the screen can explain a 403, 409 or 422 in plain words.
export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, leaderId?: number, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (leaderId !== undefined) headers.set("X-Leader-Id", String(leaderId));

  const res = await fetch(`${API_URL}${path}`, { ...init, headers });
  if (!res.ok) throw new ApiError(res.status, `${init.method ?? "GET"} ${path} failed: ${res.status}`);
  return res.json();
}

export function listEmployees(): Promise<Employee[]> {
  return request("/employees");
}

export function listSubordinates(leaderId: number): Promise<Subordinate[]> {
  return request("/subordinates", leaderId);
}

export function listQuestions(): Promise<Question[]> {
  return request("/questions");
}

export function listEvaluations(leaderId: number, employeeId: number): Promise<Evaluation[]> {
  return request(`/employees/${employeeId}/evaluations`, leaderId);
}

export function createEvaluation(leaderId: number, employeeId: number, answers: AnswerInput[]): Promise<unknown> {
  return request("/evaluations", leaderId, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ employee_id: employeeId, answers }),
  });
}
