"use client";

import { Suspense, useEffect} from "react";
import { useRouter, useSearchParams} from "next/navigation";

function CallbackHandler() {
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
    return <p style={{textAlign: "center", marginTop: "4rem"}}>Se conecteaza...</p>
}

export default function AuthCallback() {
    return (
        <Suspense fallback={<p style={{textAlign: "center", marginTop:"4rem"}}>Se incarca...</p>}>
            <CallbackHandler />
        </Suspense>
    )
}