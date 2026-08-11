"use client";

import { useEffect} from "react";
import { useRouter, useSearchParams} from "next/navigation";

export default function AuthCallback() {
    const router = useRouter();
    const searchParams = useSearchParams();

    useEffect(() => {
        const token = searchParams.get("token");
        if (token) {
            localStorage.setItem("jwt_token", token);
            router.replace("/dashboard");
        } else {
            router.replace("/");
        }
    }, [searchParams, router]);
    return <p style={{ textAlign: "center", marginTop: "4rem" }}>Se conecteaza...</p>;
}