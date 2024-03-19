# FastAPI Backend 

## Features:

- FastAPI project structure tree
- user module
  - id, username, **email**, **password**, role, is_active, created_at, updated_at
- admin dashboard => sqladmin
- authentication => JWT
- db migration => alembic 
- CORS middleware 

## Structured Tree

```sh
├── alembic     # 데이터베이스 마이그레이션 관리
├── alembic.ini
├── app
│   ├── api
│   │   ├── endpoints   # 각 기능(사용자, 제품, 결제)에 대한 모듈이 포함되어 있습니다.
│   │   │   ├── __init__.py
│   │   │   └── user
│   │   │       ├── auth.py
│   │   │       ├── functions.py
│   │   │       ├── __init__.py
│   │   │       └── user.py
│   │   ├── __init__.py
│   │   └── routers     # 각 라우터가 기능에 해당하는 FastAPI 라우터를 포함합니다.
│   │       ├── api.py
│   │       ├── __init__.py
│   │       └── user.py
│   ├── core    # 데이터베이스 관리, 종속성 등과 같은 핵심 기능을 포함합니다.
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── __init__.py
│   ├── main.py     # FastAPI 앱을 초기화하고 다양한 구성 요소를 결합합니다.
│   ├── models      # 사용자, 제품, 결제 등을 위한 데이터베이스 모델을 정의하는 모듈을 포함합니다.
│   │   ├── admin.py
│   │   ├── common.py
│   │   ├── __init__.py
│   │   └── user.py
│   ├── schemas   # 데이터 검증을 위한 Pydantic 모델
│   │   ├── __init__.py
│   │   └── user.py
│   └── utils       # 다양한 기능에 걸쳐 사용되는 유틸리티 기능을 포함할 수 있습니다.
├── requirements.txt # 프로젝트 종속성 목록.
```

**app/api/endpoints/**: 각 기능(사용자, 제품, 결제)에 대한 모듈을 포함합니다.

**app/api/routers/**: 각 라우터가 기능에 해당하는 FastAPI 라우터를 포함합니다.

**app/models/**: 사용자, 제품, 결제 등에 대한 데이터베이스 모델을 정의하는 모듈이 포함되어 있습니다.

**app/core/**: 데이터베이스 관리, 종속성 등과 같은 핵심 기능이 포함되어 있습니다.

**app/utils/**: 다양한 기능에 걸쳐 사용되는 유틸리티 기능을 포함할 수 있습니다.

**app/main.py**: FastAPI 앱을 초기화하고 다양한 구성 요소를 통합합니다.

**tests/**: 테스트 케이스를 보관합니다.

**alembic/**: 데이터베이스 마이그레이션을 관리합니다.

**docs/**: 문서 파일을 보관합니다.

**scripts/**: 유틸리티 스크립트가 포함되어 있습니다.

**requirements.txt**: 프로젝트 종속성을 나열합니다.


# Setup

가장 먼저 할 일은 저장소를 복제하는 것입니다.

```sh
$
```

종속성을 설치하고 활성화할 가상 환경을 만듭니다.:

```sh
$ 
$ python -m venv venv
$ source venv/bin/activate
```

그런 다음 종속성을 설치합니다.:

```sh
# for fixed version (업데이트 예정)
(venv)$ pip install -r requirements.txt

# or for updated version
(venv)$ pip install -r dev.txt
```


`pip` 종속성 다운로드가 완료되면 다음을 수행합니다.

```sh
# db migrations
(venv)$ alembic upgrade head

# start the server
(venv)$ uvicorn app.main:app --reload
```

## User module's API (삭제 예정)

| SRL | METHOD   | ROUTE              | FUNCTIONALITY                  | Fields                                                                                |
| --- | -------- | ------------------ | ------------------------------ | ------------------------------------------------------------------------------------- |
| _1_ | _POST_   | `/login`           | _Login user_                   | _**email**, **password**_                                                             |
| _2_ | _POST_   | `/users/`          | _Create new user_              | _**email**, **password**, first name, last name_                                      |
| _3_ | _GET_    | `/users/`          | _Get all users list_           | _email, password, first name, last name, role, is_active, created_at, updated_at, id_ |
| _4_ | _GET_    | `/users/me/`       | _Get current user details_     | _email, password, first name, last name, role, is_active, created_at, updated_at, id_ |
| _5_ | _GET_    | `/users/{user_id}` | _Get indivisual users details_ | _email, password, first name, last name, role, is_active, created_at, updated_at, id_ |
| _6_ | _PATCH_  | `/users/{user_id}` | _Update the user partially_    | _email, password, is_active, role_                                                    |
| _7_ | _DELETE_ | `/users/{user_id}` | _Delete the user_              | _None_                                                                                |
| _8_ | _GET_    | `/`                | _Home page_                    | _None_                                                                                |
| _9_ | _GET_    | `/admin`           | _Admin Dashboard_              | _None_                                                                                |

# Tools

### Back-end

#### Language:

    Python

#### Frameworks:

    FastAPI
    pydantic

#### Other libraries / tools:

    SQLAlchemy
    starlette
    uvicorn
    python-jose
    alembic
