import Layout from "../components/Layout";

function Dashboard() {
  return (
    <Layout>

<section className="py-5" style={{marginTop:"70px"}}>
<div className="container">

{/* Welcome Header */}
<div className="row mb-4">
<div className="col-12">
<div className="glass-card p-4">
<div className="d-flex align-items-center justify-content-between flex-wrap gap-3">

<div>
<h3 className="fw-bold mb-1">Welcome back! 👋</h3>
<p className="text-muted mb-0">
Your roommate dashboard
</p>
</div>

<div className="d-flex gap-2">
<a href="/edit-profile" className="btn btn-outline-secondary btn-sm">
Edit Profile
</a>

<a href="/search" className="btn btn-accent btn-sm">
Find Matches
</a>
</div>

</div>
</div>
</div>
</div>


{/* Stats */}
<div className="row g-3 mb-4">

<div className="col-6 col-md-3">
<div className="glass-card p-3 text-center h-100">
<i className="bi bi-people-fill text-accent display-6"></i>
<h4 className="fw-bold mt-2 mb-0">12</h4>
<small className="text-muted">Matches</small>
</div>
</div>

<div className="col-6 col-md-3">
<div className="glass-card p-3 text-center h-100">
<i className="bi bi-star-fill text-warning display-6"></i>
<h4 className="fw-bold mt-2 mb-0">4.5</h4>
<small className="text-muted">Rating</small>
</div>
</div>

<div className="col-6 col-md-3">
<div className="glass-card p-3 text-center h-100">
<i className="bi bi-chat-quote-fill text-info display-6"></i>
<h4 className="fw-bold mt-2 mb-0">5</h4>
<small className="text-muted">Reviews</small>
</div>
</div>

<div className="col-6 col-md-3">
<div className="glass-card p-3 text-center h-100">
<i className="bi bi-geo-alt-fill text-success display-6"></i>
<h4 className="fw-bold mt-2 mb-0">8</h4>
<small className="text-muted">Nearby</small>
</div>
</div>

</div>


{/* Quick Actions */}
<div className="row g-3 mt-3">

<div className="col-md-3">
<a href="/map" className="glass-card p-3 d-flex align-items-center gap-3 text-decoration-none text-white quick-action">
<i className="bi bi-geo-alt-fill text-success fs-3"></i>
<div>
<strong>Explore Map</strong>
<br/>
<small className="text-muted">Find nearby roommates</small>
</div>
</a>
</div>

<div className="col-md-3">
<a href="/compare" className="glass-card p-3 d-flex align-items-center gap-3 text-decoration-none text-white quick-action">
<i className="bi bi-bar-chart-line-fill text-info fs-3"></i>
<div>
<strong>Compare Tool</strong>
<br/>
<small className="text-muted">Side-by-side analysis</small>
</div>
</a>
</div>

<div className="col-md-3">
<a href="/reviews" className="glass-card p-3 d-flex align-items-center gap-3 text-decoration-none text-white quick-action">
<i className="bi bi-star-fill text-warning fs-3"></i>
<div>
<strong>Reviews</strong>
<br/>
<small className="text-muted">User feedback</small>
</div>
</a>
</div>

<div className="col-md-3">
<a href="/chatbot" className="glass-card p-3 d-flex align-items-center gap-3 text-decoration-none text-white quick-action">
<i className="bi bi-chat-dots-fill text-accent fs-3"></i>
<div>
<strong>AI Assistant</strong>
<br/>
<small className="text-muted">Get roommate tips</small>
</div>
</a>
</div>

</div>


{/* Floating Chat Button */}

<div className="chat-widget">

<button className="chat-widget-btn">
<i className="bi bi-chat-dots-fill"></i>
</button>

</div>

</div>
</section>

</Layout>
  );
}

export default Dashboard;