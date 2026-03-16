import Layout from "../components/Layout";

function Home() {
  return (
    <Layout>

      {/* HERO SECTION */}
      <section className="hero-section d-flex align-items-center position-relative" id="hero">

        <canvas id="particles-canvas"></canvas>

        <div className="container position-relative" style={{ zIndex: 1 }}>
          <div className="row align-items-center">

            <div className="col-lg-7">

              <span className="badge bg-accent bg-opacity-10 text-accent px-3 py-2 rounded-pill">
                AI-Powered Roommate Matching
              </span>

              <h1 className="display-3 fw-800 mt-3">
                Find Your <span className="text-accent">Perfect</span> Roommate Match
              </h1>

              <p className="lead text-muted mt-3">
                CohabitAI uses advanced compatibility algorithms and geo-spatial
                analytics to match you with ideal roommates.
              </p>

              <div className="d-flex gap-3 mt-4">

                <a href="/register" className="btn btn-accent btn-lg">
                  Get Started Free
                </a>

                <a href="#features" className="btn btn-outline-light btn-lg">
                  How It Works
                </a>

              </div>

            </div>

          </div>
        </div>

      </section>


      {/* TRUSTED SECTION */}
      <section className="py-4 border-bottom border-secondary border-opacity-10">
        <div className="container text-center">

          <span className="me-4">SSL Encrypted</span>
          <span className="me-4">Verified Profiles</span>
          <span className="me-4">Real-Time Matching</span>
          <span className="me-4">50+ Cities</span>
          <span>10K+ Users</span>

        </div>
      </section>


      {/* FEATURES SECTION */}
      <section id="features" className="py-5">

        <div className="container">

          <div className="text-center mb-5">
            <h2>How CohabitAI Works</h2>
          </div>

          <div className="row g-4">

            <div className="col-md-3">
              <div className="glass-card p-4 text-center">
                <h5>Geo Discovery</h5>
                <p>Find roommates nearby using interactive map.</p>
              </div>
            </div>

            <div className="col-md-3">
              <div className="glass-card p-4 text-center">
                <h5>AI Matching</h5>
                <p>Compatibility based on lifestyle preferences.</p>
              </div>
            </div>

            <div className="col-md-3">
              <div className="glass-card p-4 text-center">
                <h5>Compare Tool</h5>
                <p>Compare profiles side-by-side.</p>
              </div>
            </div>

            <div className="col-md-3">
              <div className="glass-card p-4 text-center">
                <h5>AI Chatbot</h5>
                <p>Get advice on finding the right roommate.</p>
              </div>
            </div>

          </div>

        </div>

      </section>


      {/* CTA SECTION */}
      <section className="py-5">

        <div className="container text-center">

          <h2>Ready to Find Your Ideal Roommate?</h2>

          <p className="text-muted">
            Join thousands of residents using CohabitAI.
          </p>

          <a href="/register" className="btn btn-accent btn-lg mt-3">
            Create Your Profile
          </a>

        </div>

      </section>


    </Layout>
  );
}

export default Home;