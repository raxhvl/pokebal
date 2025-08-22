# PokéBAL

A web application that tracks the adoption and implementation status of Block Access Lists (BAL) across different Ethereum execution clients. It provides a visual dashboard showing which test cases pass, fail, or are still pending for each client.

## Tech Stack

- **Framework**: Next.js 15 with TypeScript
- **Styling**: Tailwind CSS with shadcn/ui components
- **Build Tool**: Next.js built-in bundler
- **Deployment**: Static site generation ready

## Quick Start

1. **Install dependencies**:

   ```bash
   npm install
   ```

2. **Start development server**:

   ```bash
   npm run dev
   ```

3. **Build for production**:

   ```bash
   npm run build
   ```

## Test Case Management

### Syncing Test Cases

The application automatically syncs test cases from the [Ethereum Execution Spec Tests repository](https://github.com/ethereum/execution-spec-tests/).

Run the sync script:

```bash
npm run sync-tests
```

### How It Works

1. **Fetches** the latest markdown checklist from the GitHub repository
2. **Parses** the markdown table into structured JSON data
3. **Validates** the table format and content
4. **Merges** new test cases with existing results
5. **Updates** `src/data/test_results.json` with the latest data

### Test Case Structure

Each test case includes:

- **ID**: Function name from the test specification
- **Description**: What the test validates
- **Setup**: Initial conditions for the test
- **Expectation**: Expected behavior or outcome
- **Status**: `completed` or `planned`
- **Results**: Per-client test results (`pass`, `fail`, `pending`)

## Configuration

Test case source and other settings are configured in `src/config/app.ts`:

## Project Structure

```
src/
├── app/                   # Next.js app router pages
├── components/            # React components
│   ├── TestResultsTable.tsx
│   ├── MobileTestCard.tsx
│   ├── StatusIcon.tsx
│   └── ...
├── config/               # Configuration files
├── data/                 # JSON data files
├── types/                # TypeScript type definitions
└── utils/                # Utility functions

scripts/
└── sync-test-cases.ts    # Test case synchronization script
```

## Development

### Adding New Clients

1. Update `src/data/clients.json` with client information
2. Add client logo to `public/img/logos/`
3. Update test results in `src/data/test_results.json`

### Updating Test Results

Test results can be updated manually in `src/data/test_results.json` or by running the sync script to refresh test case definitions.

## Contributing

1. **Test Cases**: Contribute new test cases via the [Ethereum Execution Spec Tests repository](https://github.com/ethereum/execution-spec-tests)
2. **Implementation Results**: Update client implementation status by modifying test results
3. **Features**: Submit pull requests for new features or improvements
