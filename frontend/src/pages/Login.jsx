import Layout from "../components/Layout";

function Login() {
  return (
    <Layout>

      <div className="container py-5">

        <h2 className="mb-4">Login</h2>

        <form>

          <div className="mb-3">
            <label className="form-label">Email</label>
            <input type="email" className="form-control" />
          </div>

          <div className="mb-3">
            <label className="form-label">Password</label>
            <input type="password" className="form-control" />
          </div>

          <button className="btn btn-primary">
            Login
          </button>

        </form>

      </div>

    </Layout>
  );
}

export default Login;