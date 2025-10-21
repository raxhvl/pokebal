import { NextRequest, NextResponse } from "next/server";
import testResultsData from "@/data/test_results.json";
import clientsData from "@/data/clients.json";
import { getOverallAdoptionStats } from "@/lib/utils";
import { TestResults, Clients } from "@/types";

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ eip: string }> }
) {
  const { eip: eipNumber } = await params;

  // Currently only supporting EIP-7928
  if (eipNumber !== "7928") {
    return NextResponse.json(
      { error: "EIP not found", eip: eipNumber },
      { status: 404 }
    );
  }

  const { tests, lastUpdated, spec } = testResultsData as TestResults;
  const clients = clientsData as Clients;

  // Calculate statistics using existing utility
  const stats = getOverallAdoptionStats(tests, clients);

  // Count active clients (clients with at least one result)
  const activeClients = stats.clientStats.filter(
    (client) => client.total > 0 && (client.passed > 0 || client.failed > 0)
  ).length;

  // Transform response to match API schema
  const response = {
    eip: eipNumber,
    spec,
    lastUpdated,
    summary: {
      totalClients: stats.totalClients,
      activeClients,
      totalTests: stats.totalTests,
      totalVariants: stats.totalVariants,
      overallScore: Math.round(stats.overallPassRate * 10) / 10,
    },
    clients: stats.clientStats.map((clientStat) => {
      const clientInfo = clients.find((c) => c.id === clientStat.clientId);
      return {
        name: clientInfo?.name || clientStat.clientId,
        version: clientInfo?.version || "unknown",
        githubRepo: clientInfo?.githubRepo,
        result: {
          passed: clientStat.passed,
          failed: clientStat.failed,
          pending: clientStat.pending,
          total: clientStat.total,
          score: Math.round(clientStat.passRate * 10) / 10,
        },
      };
    }),
  };

  return NextResponse.json(response, {
    headers: {
      "Cache-Control": "public, max-age=300, s-maxage=3600",
      "Access-Control-Allow-Origin": "*",
    },
  });
}
