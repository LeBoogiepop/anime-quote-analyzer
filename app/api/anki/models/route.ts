import { NextResponse } from "next/server";

const ANKICONNECT_URL = "http://localhost:8765";

export async function GET() {
  try {
    const response = await fetch(ANKICONNECT_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        action: "modelNames",
        version: 6,
      }),
    });

    if (!response.ok) {
      throw new Error(`AnkiConnect returned ${response.status}`);
    }

    const data = await response.json();

    if (data.error) {
      return NextResponse.json(
        { error: data.error, models: [] },
        { status: 500 }
      );
    }

    return NextResponse.json({ models: data.result || [] });
  } catch (error) {
    return NextResponse.json(
      { error: "AnkiConnect not available", models: [] },
      { status: 503 }
    );
  }
}

