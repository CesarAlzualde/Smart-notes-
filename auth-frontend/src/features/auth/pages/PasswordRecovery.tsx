import PasswordRecoveryForm from '../components/PasswordRecoveryForm';

const PasswordRecovery = () => {
  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-card">
          <div className="auth-header">
            <h1>SMART NOTES</h1>
            <p>Recupera el acceso a tu cuenta</p>
          </div>
          
          <PasswordRecoveryForm />
        </div>
      </div>
    </div>
  );
};

export default PasswordRecovery;
