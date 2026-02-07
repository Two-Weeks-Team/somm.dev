import { Wine, Trophy, Medal, Award, Star, AlertTriangle } from "lucide-react";
import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#FAF4E8] to-[#F7E7CE]">
      <main className="mx-auto max-w-4xl px-6 py-20">
        <div className="text-center">
          <div className="mb-6 inline-flex items-center justify-center rounded-full bg-[#722F37] p-4">
            <Wine className="h-12 w-12 text-[#F7E7CE]" />
          </div>
          <h1 className="mb-4 text-5xl font-bold text-[#722F37]">
            Somm
          </h1>
          <p className="mb-2 text-2xl font-light text-[#722F37]/80">
            AI Code Evaluation
          </p>
          <p className="mb-8 text-lg italic text-[#722F37]/60">
            &ldquo;Every codebase has terroir. We&apos;re here to taste it.&rdquo;
          </p>
        </div>

        <div className="mb-12 text-center">
          <p className="text-xl text-gray-700">
            Six AI sommeliers analyze your repositories from every angle—
            <br />
            structure, quality, security, and innovation.
          </p>
        </div>

        <div className="mb-12 grid gap-6 md:grid-cols-3">
          <div className="rounded-xl bg-white p-6 shadow-sm">
            <div className="mb-3 text-3xl">🏛️</div>
            <h3 className="mb-2 font-semibold text-[#722F37]">Marcel</h3>
            <p className="text-sm text-gray-600">Structure & Metrics</p>
          </div>
          <div className="rounded-xl bg-white p-6 shadow-sm">
            <div className="mb-3 text-3xl">🎭</div>
            <h3 className="mb-2 font-semibold text-[#722F37]">Isabella</h3>
            <p className="text-sm text-gray-600">Code Quality</p>
          </div>
          <div className="rounded-xl bg-white p-6 shadow-sm">
            <div className="mb-3 text-3xl">🔍</div>
            <h3 className="mb-2 font-semibold text-[#722F37]">Heinrich</h3>
            <p className="text-sm text-gray-600">Security & Testing</p>
          </div>
          <div className="rounded-xl bg-white p-6 shadow-sm">
            <div className="mb-3 text-3xl">🌱</div>
            <h3 className="mb-2 font-semibold text-[#722F37]">Sofia</h3>
            <p className="text-sm text-gray-600">Innovation</p>
          </div>
          <div className="rounded-xl bg-white p-6 shadow-sm">
            <div className="mb-3 text-3xl">🛠️</div>
            <h3 className="mb-2 font-semibold text-[#722F37]">Laurent</h3>
            <p className="text-sm text-gray-600">Implementation</p>
          </div>
          <div className="rounded-xl bg-white p-6 shadow-sm">
            <div className="mb-3 text-3xl">🎯</div>
            <h3 className="mb-2 font-semibold text-[#722F37]">Jean-Pierre</h3>
            <p className="text-sm text-gray-600">Final Verdict</p>
          </div>
        </div>

        <div className="text-center">
          <Link
            href="/evaluate"
            className="inline-block rounded-full bg-[#722F37] px-8 py-4 text-lg font-semibold text-[#F7E7CE] transition-colors hover:bg-[#5A252C]"
          >
            Begin Your Evaluation
          </Link>
        </div>

        <div className="mt-16 rounded-xl bg-white p-8 shadow-sm">
          <h2 className="mb-2 text-center text-2xl font-semibold text-[#722F37]">
            Scoring System
          </h2>
          <p className="mb-6 text-center text-sm text-gray-600">
            From legendary cellars to house wines — every codebase has its place
          </p>
          <div className="grid gap-4 text-center md:grid-cols-4">
            <div className="rounded-lg bg-gradient-to-br from-yellow-100 to-yellow-50 p-4">
              <div className="mb-1 flex justify-center"><Trophy size={28} className="text-yellow-500" /></div>
              <div className="font-bold text-yellow-700">95-100</div>
              <div className="text-sm text-yellow-600">Legendary</div>
            </div>
            <div className="rounded-lg bg-gradient-to-br from-amber-100 to-amber-50 p-4">
              <div className="mb-1 flex justify-center"><Trophy size={28} className="text-amber-600" /></div>
              <div className="font-bold text-amber-700">90-94</div>
              <div className="text-sm text-amber-600">Grand Cru</div>
            </div>
            <div className="rounded-lg bg-gradient-to-br from-orange-100 to-orange-50 p-4">
              <div className="mb-1 flex justify-center"><Medal size={28} className="text-orange-500" /></div>
              <div className="font-bold text-orange-700">85-89</div>
              <div className="text-sm text-orange-600">Premier Cru</div>
            </div>
            <div className="rounded-lg bg-gradient-to-br from-green-100 to-green-50 p-4">
              <div className="mb-1 flex justify-center"><Award size={28} className="text-green-600" /></div>
              <div className="font-bold text-green-700">80-84</div>
              <div className="text-sm text-green-600">Village</div>
            </div>
            <div className="rounded-lg bg-gradient-to-br from-blue-100 to-blue-50 p-4">
              <div className="mb-1 flex justify-center"><Star size={28} className="text-blue-500" /></div>
              <div className="font-bold text-blue-700">70-79</div>
              <div className="text-sm text-blue-600">Table Wine</div>
            </div>
            <div className="rounded-lg bg-gradient-to-br from-purple-100 to-purple-50 p-4">
              <div className="mb-1 flex justify-center"><Wine size={28} className="text-purple-500" /></div>
              <div className="font-bold text-purple-700">60-69</div>
              <div className="text-sm text-purple-600">House Wine</div>
            </div>
            <div className="rounded-lg bg-gradient-to-br from-red-100 to-red-50 p-4 md:col-span-2">
              <div className="mb-1 flex justify-center"><AlertTriangle size={28} className="text-red-500" /></div>
              <div className="font-bold text-red-700">&lt;60</div>
              <div className="text-sm text-red-600">Corked</div>
            </div>
          </div>
        </div>
      </main>

      <footer className="border-t border-[#722F37]/10 py-8 text-center text-sm text-gray-500">
        <p>© 2025 Somm.dev — AI Code Sommelier</p>
      </footer>
    </div>
  );
}
