import CompanyScorecardClient from "./CompanyScorecardClient";

// Required for Next.js static export (output: 'export').
// Returns a placeholder param so the route is included in the build.
export async function generateStaticParams() {
  return [{ cin: "_" }];
}

export const dynamicParams = false;

export default function CompanyScorecardPage() {
  return <CompanyScorecardClient />;
}
