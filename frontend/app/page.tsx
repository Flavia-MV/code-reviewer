const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
export default function Home() {
    return (
        <main style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "100vh", gap: "1rem", fontFamily: "sans-serif" }}>
            <h1>Code Reviewer</h1>
            <p>Conecteaza-ti contul de GitHub ca sa importi un repository.</p>
            <a href={`${BACKEND_URL}/auth/github/login`} style={{padding: "0.75rem 1.5rem", background: "#111", color: "#fff", borderRadius: "8px", textDecoration: "none"}}>
                Conecteaza-te cu GitHub
            </a>
        </main>
    )
}