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
          <li key={repo.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.75rem", border: "1px solid #eee", borderRadius: "8px", marginBottom: "0.5rem" }}>
            <span>
                <strong>{repo.full_name}</strong>
                <span style={{ marginLeft: "0.5rem", color: "#666" }}>({repo.index_status})</span>
            </span>
             <button onClick={() => indexRepo(repo.id)} disabled={loading}>
                 Indexeaza
             </button>
          </li>
        ))}
      </ul>
    </main>
  );
}

