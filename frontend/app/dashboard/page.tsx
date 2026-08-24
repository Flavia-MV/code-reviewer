"use client";
import { useEffect, useState} from "react";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

type Repo = {
    id: number;
    full_name: string;
    index_status: string;
};

export default function Dashboard() {
    const [repos, setRepos] = useState<Repo[]>([]);
    const [repoInput, setRepoInput] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [question, setQuestion] = useState("");
    const [answer, setAnswer] = useState<{ answer: string; sources: any[] } | null>(null);
    const [askingRepoId, setAskingRepoId] = useState<number | null>(null);
    const [asking, setAsking] = useState(false);

    const token = typeof window !== "undefined" ? localStorage.getItem("jwt_token") : null;

    async function fetchRepos() {
        const res = await fetch(`${BACKEND_URL}/repos`, {
              headers: { Authorization: `Bearer ${token}` },
            });
        if (res.ok) setRepos(await res.json());
    }

    useEffect(() => {
        if (token) fetchRepos();
    }, [token]);
    async function importRepo() {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${BACKEND_URL}/repos/import?full_name=${encodeURIComponent(repoInput)}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Import esuat");
      }
      setRepoInput("");
      await fetchRepos();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Eroare necunoscuta");
    } finally {
      setLoading(false);
    }
  }
  async function indexRepo(repoId: number) {
        setLoading(true);
        try {
            await fetch(`${BACKEND_URL}/repos/${repoId}/index`, {
                method: "POST",
                headers: { Authorization: `Bearer ${token}` },
            });
            await fetchRepos();
        } catch (e) {
            setError(e instanceof Error ? e.message : "Eroare necunoscuta");
        } finally {
            setLoading(false);
        }
    }

    async function askQuestion(repoId: number) {
        setAsking(true);
        setAnswer(null);
        try {
            const res = await fetch(
                `${BACKEND_URL}/repos/${repoId}/ask?question=${encodeURIComponent(question)}`,
                {
                    method: "POST",
                    headers: { Authorization: `Bearer ${token}` },
                }
                );
            const data = await res.json();
            setAnswer(data);
        } catch (e) {
            setError(e instanceof Error ? e.message : "Eroare necunoscuta");
        } finally {
            setAsking(false);
        }
    }

  return (
    <main style={{ maxWidth: "600px", margin: "3rem auto", fontFamily: "sans-serif" }}>
      <h1>Repo-urile tale</h1>

      <div style={{ display: "flex", gap: "0.5rem", margin: "1.5rem 0" }}>
        <input
          value={repoInput}
          onChange={(e) => setRepoInput(e.target.value)}
          placeholder="owner/repo, ex: octocat/hello-world"
          style={{ flex: 1, padding: "0.5rem" }}
        />
        <button onClick={importRepo} disabled={loading || !repoInput}>
          {loading ? "Se importa..." : "Importa"}
        </button>
      </div>

      {error && <p style={{ color: "red" }}>{error}</p>}

      <ul style={{ listStyle: "none", padding: 0 }}>
        {repos.map((repo) => (
          <li key={repo.id} style={{ padding: "0.75rem", border: "1px solid #eee", borderRadius: "8px", marginBottom: "0.5rem" }}>
              <div style={{display: "flex", justifyContent: "space-between", alignItems: "center"}}>
                <span>
                    <strong>{repo.full_name}</strong>
                    <span style={{ marginLeft: "0.5rem", color: "#666" }}>({repo.index_status})</span>
                </span>
                  <div style={{display: "flex", gap: "0.5rem"}}>
                     <button onClick={() => indexRepo(repo.id)} disabled={loading}>
                         Indexeaza
                     </button>
                      {repo.index_status === "ready" && (
                          <button onClick={() => setAskingRepoId(askingRepoId === repo.id ? null : repo.id)}>
                           Intreaba
                          </button>
                      )}
                  </div>
              </div>

              {askingRepoId === repo.id && (
                  <div style = {{marginTop: "1rem", paddingTop: "1rem", borderTop: "1px solid #eee"}}>
                      <div style={{display: "flex", gap: "0.5rem"}}>
                          <input
                              value={question}
                              onChange={(e) => setQuestion(e.target.value)}
                              placeholder="Ce vrei sa stii despre acest cod?"
                              style={{flex:1, padding: "0.5rem"}}
                              />
                          <button onClick={() => askQuestion(repo.id)} disabled={asking || !question}>
                              {asking ? "Se gandeste..." : "Trimite"}
                          </button>
                      </div>
                      {answer && (
                          <div style ={{marginTop: "1rem", paddingTop: "1rem", background: "#f7f7f7", borderRadius: "8px"}}>
                              <p>{answer.answer}</p>
                              <div style = {{marginTop: "0.5rem", fontSize: "0.85rem", color: "#666"}}>
                                  <strong>Surse:</strong>
                                  <ul>
                                      {answer.sources.map((source, i) => (
                                          <li key={i}>
                                              {source.file_path} (linii {source.start_line}-{source.end_line})
                                              {source.name && ` - ${source.name}`}
                                          </li>
                                          ))}
                                  </ul>
                              </div>
                          </div>
                      )}
                  </div>
              )}
          </li>
        ))}
      </ul>
    </main>
  );
}

