import React, { useEffect, useState } from 'react';
import { Card, Container, Row, Col, Form, Button, Alert } from 'react-bootstrap';
import { getCurrentUserProfile, updateUserProfile } from '../../../api/user';
import type { UserProfile } from '../../../api/user';

const ProfilePage: React.FC = () => {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [formValues, setFormValues] = useState({
    name: '',
    email: ''
  });
  const [editMode, setEditMode] = useState(false);
  const [updateSuccess, setUpdateSuccess] = useState(false);
  const [updateError, setUpdateError] = useState<string | null>(null);

  // Cargar datos del perfil al montar el componente
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true);
        const userData = await getCurrentUserProfile();
        setProfile(userData);
        setFormValues({
          name: userData.name || '',
          email: userData.email || ''
        });
        setError(null);
      } catch (err) {
        console.error('Error al cargar el perfil de usuario:', err);
        setError('No se pudo cargar la información del perfil. Por favor, intenta más tarde.');
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  // Manejar cambios en el formulario
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormValues({
      ...formValues,
      [name]: value
    });
  };

  // Manejar envío del formulario
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setUpdateSuccess(false);
      setUpdateError(null);
      
      const updatedProfile = await updateUserProfile({
        name: formValues.name,
        email: formValues.email
      });
      
      setProfile(updatedProfile.user);
      setEditMode(false);
      setUpdateSuccess(true);
      
      // Ocultar mensaje de éxito después de 3 segundos
      setTimeout(() => {
        setUpdateSuccess(false);
      }, 3000);
      
    } catch (err: any) {
      setUpdateError(err.response?.data?.error || 'No se pudo actualizar el perfil');
    }
  };

  return (
    <Container className="py-4">
      <h1 className="mb-4">Mi Perfil</h1>
      
      {loading ? (
        <p>Cargando perfil...</p>
      ) : error ? (
        <Alert variant="danger">{error}</Alert>
      ) : (
        <>
          {updateSuccess && (
            <Alert variant="success">
              Perfil actualizado correctamente
            </Alert>
          )}
          
          {updateError && (
            <Alert variant="danger">
              {updateError}
            </Alert>
          )}
          
          <Card>
            <Card.Header className="d-flex justify-content-between align-items-center">
              <h4 className="mb-0">Información Personal</h4>
              {!editMode ? (
                <Button variant="outline-primary" onClick={() => setEditMode(true)}>
                  Editar
                </Button>
              ) : null}
            </Card.Header>
            <Card.Body>
              {editMode ? (
                <Form onSubmit={handleSubmit}>
                  <Form.Group className="mb-3">
                    <Form.Label>Nombre</Form.Label>
                    <Form.Control
                      type="text"
                      name="name"
                      value={formValues.name}
                      onChange={handleChange}
                    />
                  </Form.Group>
                  
                  <Form.Group className="mb-3">
                    <Form.Label>Email</Form.Label>
                    <Form.Control
                      type="email"
                      name="email"
                      value={formValues.email}
                      onChange={handleChange}
                    />
                  </Form.Group>
                  
                  <div className="d-flex gap-2">
                    <Button variant="primary" type="submit">
                      Guardar Cambios
                    </Button>
                    <Button variant="outline-secondary" onClick={() => {
                      setEditMode(false);
                      // Restaurar valores originales
                      if (profile) {
                        setFormValues({
                          name: profile.name || '',
                          email: profile.email || ''
                        });
                      }
                    }}>
                      Cancelar
                    </Button>
                  </div>
                </Form>
              ) : profile ? (
                <Row>
                  <Col md={6}>
                    <p><strong>Nombre de usuario:</strong> {profile.username}</p>
                    <p><strong>Nombre:</strong> {profile.name || 'No especificado'}</p>
                    <p><strong>Email:</strong> {profile.email}</p>
                    <p><strong>Miembro desde:</strong> {new Date(profile.created_at).toLocaleDateString()}</p>
                  </Col>
                </Row>
              ) : null}
            </Card.Body>
          </Card>
          
          <Card className="mt-4">
            <Card.Header>
              <h4 className="mb-0">Configuración de seguridad</h4>
            </Card.Header>
            <Card.Body>
              <p>Aquí podrás cambiar tu contraseña o actualizar tus preguntas de seguridad.</p>
              <Button variant="outline-secondary">
                Cambiar Contraseña
              </Button>
            </Card.Body>
          </Card>
        </>
      )}
    </Container>
  );
};

export default ProfilePage;
