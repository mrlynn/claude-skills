import { NextRequest } from "next/server";
import { auth } from "@/lib/auth";
import { connectToDatabase } from "@/lib/db/connection";
// import { YourModel } from "@/lib/db/models/YourModel";
// import { yourSchema } from "@/lib/db/schemas";
import { errorResponse, successResponse } from "@/lib/utils";

export async function GET() {
  try {
    const session = await auth();
    if (!session?.user) {
      return errorResponse("Unauthorized", 401);
    }

    await connectToDatabase();

    // const items = await YourModel.find().sort({ createdAt: -1 }).lean();
    // return successResponse(items);

    return successResponse({ message: "OK" });
  } catch (error) {
    console.error("GET /api/your-route error:", error);
    return errorResponse("Internal server error", 500);
  }
}

export async function POST(request: NextRequest) {
  try {
    const session = await auth();
    const role = (session?.user as { role?: string })?.role;
    if (!role || !["admin", "super_admin"].includes(role)) {
      return errorResponse("Forbidden", 403);
    }

    const body = await request.json();

    // Validate with Zod
    // const parsed = yourSchema.safeParse(body);
    // if (!parsed.success) {
    //   return errorResponse(parsed.error.errors[0].message, 422);
    // }

    await connectToDatabase();

    // const item = await YourModel.create(parsed.data);
    // return successResponse(item, 201);

    return successResponse({ message: "Created" }, 201);
  } catch (error) {
    console.error("POST /api/your-route error:", error);
    return errorResponse("Internal server error", 500);
  }
}

export async function PATCH(request: NextRequest) {
  try {
    const session = await auth();
    const role = (session?.user as { role?: string })?.role;
    if (!role || !["admin", "super_admin"].includes(role)) {
      return errorResponse("Forbidden", 403);
    }

    const body = await request.json();

    // const parsed = updateYourSchema.safeParse(body);
    // if (!parsed.success) {
    //   return errorResponse(parsed.error.errors[0].message, 422);
    // }

    await connectToDatabase();

    // const item = await YourModel.findByIdAndUpdate(id, parsed.data, { new: true }).lean();
    // if (!item) return errorResponse("Not found", 404);
    // return successResponse(item);

    return successResponse({ message: "Updated" });
  } catch (error) {
    console.error("PATCH /api/your-route error:", error);
    return errorResponse("Internal server error", 500);
  }
}

export async function DELETE(request: NextRequest) {
  try {
    const session = await auth();
    const role = (session?.user as { role?: string })?.role;
    if (role !== "super_admin") {
      return errorResponse("Forbidden", 403);
    }

    await connectToDatabase();

    // const item = await YourModel.findByIdAndDelete(id);
    // if (!item) return errorResponse("Not found", 404);
    // return successResponse({ message: "Deleted" });

    return successResponse({ message: "Deleted" });
  } catch (error) {
    console.error("DELETE /api/your-route error:", error);
    return errorResponse("Internal server error", 500);
  }
}
