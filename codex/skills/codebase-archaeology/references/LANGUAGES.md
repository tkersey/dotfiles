# Language-Specific Archaeology Searches

Use these commands as starting points. Adapt to the repository layout and avoid exhaustive scans when a targeted search will answer the question.

## Rust

```bash
rg -n "fn main\(|#\[(tokio|async_std)::main\]" src crates
rg -n "clap::|derive\(.*Parser|Subcommand|Args" src crates
rg -n "^pub (struct|enum|trait) |^struct |^enum |^trait " src crates
rg -n "impl .* for |impl [A-ZA-Za-z0-9_]+" src crates
rg -n "thiserror|anyhow|eyre|serde::Deserialize|std::env|env::var|config|settings" Cargo.toml src crates
rg -n "sqlx|rusqlite|diesel|reqwest|tonic|axum|actix|warp|query\(|execute\(|File::|fs::" Cargo.toml src crates
```

## TypeScript / JavaScript

```bash
rg -n "createRoot|NextResponse|route\.ts|express\(|fastify\(|Router\(|app\.(get|post|put|delete|use)|export default|module\.exports" src app pages server
rg -n "commander|program\.(command|option|argument)|yargs|meow|oclif" package.json src bin
rg -n "^export (interface|type|class) |^interface |^type |z\.object|yup\.object|class-validator|Prisma" src app packages
rg -n "process\.env|dotenv|envsafe|envalid|@t3-oss/env|config\(|getConfig|loadConfig" src app packages
rg -n "prisma|drizzle|typeorm|sequelize|knex|mongoose|redis|fetch\(|axios|graphql|stripe|s3|kafka" package.json src app packages
```

## Python

```bash
rg -n "if __name__ == ['\"]__main__['\"]|def main\(|FastAPI\(|Flask\(|APIRouter|@app\.|@router\." .
rg -n "argparse|click|typer|@click\.command|@app\.command|add_argument\(" pyproject.toml setup.py requirements*.txt src
rg -n "^class [A-ZA-Za-z0-9_]+|@dataclass|BaseModel|TypedDict|Enum\(" src
rg -n "os\.environ|os\.getenv|BaseSettings|pydantic.*Settings|dynaconf|settings|config" src
rg -n "sqlalchemy|psycopg|sqlite3|pymongo|redis|requests\.|httpx|aiohttp|boto3|celery|kafka" pyproject.toml requirements*.txt src
```

## Go

```bash
rg -n "func main\(" cmd .
rg -n "cobra|flag\.|urfave/cli|http\.HandleFunc|mux\.Handle|gin\.Default|chi\.NewRouter|echo\.New" .
rg -n "^type [A-ZA-Za-z0-9_]+ struct|^type [A-ZA-Za-z0-9_]+ interface" .
rg -n "os\.Getenv|viper\.|envconfig|yaml|json|toml" .
rg -n "database/sql|gorm|sqlx|pgx|redis|http\.Client|grpc|s3|kafka|nats" go.mod .
```

## Java / Kotlin

```bash
rg -n "public static void main|fun main|@SpringBootApplication|@RestController|@Controller|@RequestMapping|@GetMapping|@PostMapping" src
rg -n "class [A-Z]|interface [A-Z]|data class|record [A-Z]|enum class|enum [A-Z]" src
rg -n "@Entity|JpaRepository|CrudRepository|Repository|Service|Component" src
rg -n "@Configuration|@Value|application\.(yml|yaml|properties)|System\.getenv|WebClient|RestTemplate|Kafka|S3|Redis" src build.gradle* pom.xml
```

## C# / .NET

```bash
rg -n "static void Main|WebApplication\.CreateBuilder|MapGet|MapPost|ControllerBase|\[Http(Get|Post|Put|Delete)\]|IHostedService" .
rg -n "^(public )?(class|record|interface|enum) [A-ZA-Za-z0-9_]+" .
rg -n "IConfiguration|appsettings\.json|Environment\.GetEnvironmentVariable|DbContext|HttpClient|MassTransit|Azure|AWS|Redis" .
```

## Ruby / Rails

```bash
rg -n "Rails\.application\.routes|resources |namespace |class .*Controller" config app
rg -n "class [A-Z].* < ApplicationRecord|belongs_to|has_many|has_one|validates" app/models
rg -n "ApplicationJob|Sidekiq|perform\(|ENV\[|credentials|Faraday|Net::HTTP|Redis" app config Gemfile
```

## PHP / Laravel

```bash
rg -n "Route::(get|post|put|delete|resource)|class .*Controller|extends Command" routes app
rg -n "class [A-Z].* extends Model|belongsTo|hasMany|fillable|casts" app
rg -n "env\(|config\(|DB::|Http::|Guzzle|Redis|Queue|Storage::" app config composer.json
```
