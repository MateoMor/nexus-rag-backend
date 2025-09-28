# Nexus RAG Backend

Backend API para aplicación RAG (Retrieval-Augmented Generation) construido con FastAPI y LlamaIndex.

## 🚀 Características

- **FastAPI**: Framework web moderno y rápido
- **LlamaIndex**: Motor RAG para procesamiento de documentos
- **ChromaDB**: Base de datos vectorial
- **OpenAI**: Integración con modelos GPT
- **Documentación automática**: Swagger UI y ReDoc
- **Tipado estático**: Pydantic para validación de datos

## 📁 Estructura del Proyecto

```
src/
├── main.py              # Punto de entrada de la aplicación
├── core/                # Configuraciones principales
├── api/v1/              # Endpoints de la API
├── services/            # Lógica de negocio
├── models/              # Modelos Pydantic
└── utils/               # Utilidades
```

## 🛠️ Instalación

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd nexus-rag-backend
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus valores
```

## 🔧 Configuración

Configura las siguientes variables en tu archivo `.env`:

```bash
# OpenAI
OPENAI_API_KEY=tu_api_key_aqui

# Security
SECRET_KEY=tu_secret_key_aqui

# Object Storage (Cloudflare R2)
R2_ACCOUNT_ID=tu_account_id_de_r2
R2_ACCESS_KEY_ID=tu_access_key
R2_SECRET_ACCESS_KEY=tu_secret_key
R2_BUCKET_NAME=tu_bucket
# Opcional dependiendo de tu setup
R2_PUBLIC_BASE_URL=https://tu-dominio-publico.example.com
R2_ENDPOINT_URL=https://tu_account_id.r2.cloudflarestorage.com

# Opcional: personalizar otros valores
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

## 🚀 Ejecución

### Desarrollo
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Producción
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## 📚 API Documentation

Una vez ejecutando, accede a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔗 Endpoints Principales

### Health Check
- `GET /api/v1/health/` - Verificar estado del servicio

### Chat
- `POST /api/v1/chat/` - Enviar mensaje al sistema RAG

### Documentos
- `POST /api/v1/documents/upload` - Subir documento
- `GET /api/v1/documents/` - Listar documentos
- `DELETE /api/v1/documents/{id}` - Eliminar documento

## 🧪 Testing

```bash
pytest
```

## 📝 TODO

- [ ] Implementar servicio RAG completo con LlamaIndex
- [ ] Integrar ChromaDB para almacenamiento vectorial
- [ ] Añadir autenticación JWT
- [ ] Implementar procesamiento de diferentes tipos de documentos
- [ ] Añadir métricas y monitoreo
- [ ] Dockerizar la aplicación

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request