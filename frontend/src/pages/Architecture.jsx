import Layout from "../components/Layout";

function Architecture() {
  return (
    <Layout>

      <section className="py-5" style={{marginTop:"80px"}}>
        <div className="container">

          <h1 className="fw-bold mb-4">
            CohabitAI System Architecture
          </h1>

          <p className="lead text-muted mb-5">
            This page explains the engineering architecture behind the
            AI-powered roommate matching platform.
          </p>


          {/* PHASE 1 */}
          <div className="glass-card p-4 mb-4">
            <h4 className="fw-bold mb-3">
              Phase 1 — Mathematical Model
            </h4>

            <p className="text-muted">
              The system represents each user as a feature vector
              containing lifestyle, personality and constraint
              attributes.
            </p>

            <pre className="arch-code">
P = [ Lifestyle | Personality | Constraints ]
            </pre>
          </div>


          {/* PHASE 2 */}
          <div className="glass-card p-4 mb-4">
            <h4 className="fw-bold mb-3">
              Phase 2 — Database Design
            </h4>

            <p className="text-muted">
              User profiles store raw persona data. Feature vectors
              are computed dynamically for flexibility.
            </p>
          </div>


          {/* PHASE 3 */}
          <div className="glass-card p-4 mb-4">
            <h4 className="fw-bold mb-3">
              Phase 3 — ML Compatibility Engine
            </h4>

            <p className="text-muted">
              A weighted cosine similarity algorithm computes the
              compatibility score between two users.
            </p>

            <pre className="arch-code">
Similarity(A,B) =
Σ(wi * Ai * Bi) /
√(Σ(wi * Ai²) * Σ(wi * Bi²))
            </pre>
          </div>


          {/* PHASE 4 */}
          <div className="glass-card p-4 mb-4">
            <h4 className="fw-bold mb-3">
              Phase 4 — Service Layer
            </h4>

            <p className="text-muted">
              The ML engine is wrapped inside independent services
              like matchmaking, compare module and chatbot.
            </p>
          </div>


          {/* PHASE 5 */}
          <div className="glass-card p-4 mb-4">
            <h4 className="fw-bold mb-3">
              Phase 5 — API Layer
            </h4>

            <p className="text-muted">
              Flask APIs expose endpoints such as:
            </p>

            <ul>
              <li>/create-user</li>
              <li>/get-matches</li>
              <li>/compare-users</li>
              <li>/start-chat</li>
              <li>/api/map-search</li>
            </ul>
          </div>


          {/* CTA */}
          <div className="text-center mt-5">

            <a href="/register" className="btn btn-accent btn-lg me-3">
              Get Started
            </a>

            <a href="/" className="btn btn-outline-light btn-lg">
              Back to Home
            </a>

          </div>

        </div>
      </section>

    </Layout>
  );
}

export default Architecture;