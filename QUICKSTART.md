# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: View the Demo

The project includes a complete example demonstrating the transformation of legacy code into modern microservices.

**Legacy Code Location:** `legacy_code/monolithic_app.py`
- 145 lines of tightly-coupled monolithic code
- Global variables and poor structure
- Mixed responsibilities

### Step 2: Run the Modernization Tool

You have two options:

#### Option A: Using the Demo Script (Recommended)
```bash
python demo.py
```

This will:
- Analyze the legacy code
- Generate microservices
- Create tests and documentation
- Show detailed progress

#### Option B: Using the CLI
```bash
python modernize.py ./legacy_code
```

With options:
```bash
python modernize.py ./legacy_code --output ./my_output --verbose
```

### Step 3: Explore the Results

After running the tool, check the `output/` directory:

```
output/
├── services/           # 5 microservices + shared models
├── api/               # API Gateway
├── docs/              # Complete documentation
└── README.md          # Setup instructions
```

## 📖 What Gets Generated

### Microservices (FastAPI)
1. **User Service** - Authentication & user management
2. **Product Service** - Catalog & inventory
3. **Order Service** - Order processing
4. **Payment Service** - Payment handling
5. **Reporting Service** - Analytics

### API Gateway
- Single entry point for all services
- Request routing
- Health monitoring

### Documentation
- Complete README with setup instructions
- Modernization roadmap (10-step plan)
- Dependency map with diagrams
- Architecture documentation
- API reference

### Tests
- Unit tests for each service
- Pytest configuration
- Test fixtures

## 🎯 Key Transformations

| Before (Legacy) | After (Modern) |
|----------------|----------------|
| 1 monolithic file | 5 microservices |
| Global variables | Dependency injection |
| MD5 hashing | Bcrypt security |
| No tests | Full test suite |
| No documentation | Comprehensive docs |
| Tight coupling | Loose coupling |
| SQLite inline | SQLAlchemy ORM |

## 🔍 Explore the Code

### Compare Before & After

**Before:**
```python
# legacy_code/monolithic_app.py
db_connection = None  # Global variable
current_user = None   # Global state

class LegacyECommerceApp:
    def register_user(self, username, password, email):
        hashed = hashlib.md5(password.encode()).hexdigest()  # Weak
        # Everything mixed together...
```

**After:**
```python
# output/services/userservice/main.py
from fastapi import FastAPI, Depends
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"])  # Strong

@app.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(user.password)
    # Clean, focused, testable
```

## 📚 Next Steps

1. **Read the Documentation**
   ```bash
   cat output/README.md
   cat output/docs/modernization_roadmap.md
   ```

2. **Review the Architecture**
   ```bash
   cat output/docs/architecture.md
   ```

3. **Check the API Documentation**
   ```bash
   cat output/docs/api_documentation.md
   ```

4. **Understand Dependencies**
   ```bash
   cat output/docs/dependency_map.md
   ```

## 🧪 Testing (Optional)

If you want to actually run the generated services:

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run a Service**
   ```bash
   cd output/services/userservice
   python main.py
   ```

3. **Access API Documentation**
   Open browser: http://localhost:8001/docs

4. **Run Tests**
   ```bash
   cd output
   pip install -r test_requirements.txt
   pytest -v
   ```

## 💡 Understanding the Tool

### How It Works

1. **Analysis Phase**
   - Scans Python files using AST
   - Identifies classes, functions, and patterns
   - Detects responsibilities and dependencies

2. **Planning Phase**
   - Generates modernization roadmap
   - Maps service dependencies
   - Identifies issues and improvements

3. **Generation Phase**
   - Creates microservice structure
   - Generates FastAPI endpoints
   - Writes database models
   - Creates tests and documentation

### Key Components

- **`modernizer/analyzer.py`** - Code analysis engine
- **`modernizer/refactorer.py`** - Service generation
- **`modernizer/test_generator.py`** - Test creation
- **`modernizer/doc_generator.py`** - Documentation
- **`modernizer/cli.py`** - Command-line interface

## 🎓 Learning Path

1. **Start Here**: Read this QUICKSTART.md
2. **Run Demo**: Execute `python demo.py`
3. **Explore Output**: Check `output/` directory
4. **Read Docs**: Review generated documentation
5. **Compare Code**: Legacy vs Modern
6. **Understand Architecture**: Read architecture.md
7. **Try It**: Run the services locally

## 🔧 Customization

To use with your own legacy code:

1. Place your legacy Python files in a directory
2. Run: `python modernize.py /path/to/your/code`
3. Review and adjust generated code as needed
4. The tool provides a starting point, not a final solution

## ⚠️ Important Notes

- This is a **Proof of Concept** for demonstration
- Generated code is a starting point, not production-ready
- Review and test all generated code
- Adjust to your specific requirements
- Use as a learning tool and accelerator

## 🎉 Success!

You now have:
- ✅ Understanding of the modernization process
- ✅ Working example of microservices architecture
- ✅ Complete documentation
- ✅ Test suite
- ✅ API Gateway
- ✅ Best practices implementation

## 📞 Need Help?

1. Check the main README.md
2. Review generated documentation
3. Examine the example code
4. Compare legacy vs modern implementations

---

**Ready to modernize your legacy code?** 🚀

Run `python demo.py` and watch the magic happen!