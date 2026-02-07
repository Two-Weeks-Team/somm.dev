import { Wine, Trophy, Medal, Award, Star, AlertTriangle, Sparkles, GitBranch, Zap, FileText, Share2, ArrowRight, ChevronDown } from "lucide-react";
import Link from "next/link";
import Image from "next/image";

const sommeliers = [
  { id: "marcel", name: "Marcel", role: "Cellar Master", desc: "Structure & Metrics", color: "#8B7355", emoji: "🏛️" },
  { id: "isabella", name: "Isabella", role: "Wine Critic", desc: "Code Quality", color: "#C41E3A", emoji: "🎭" },
  { id: "heinrich", name: "Heinrich", role: "Quality Inspector", desc: "Security & Testing", color: "#2F4F4F", emoji: "🔍" },
  { id: "sofia", name: "Sofia", role: "Vineyard Scout", desc: "Innovation & Tech", color: "#DAA520", emoji: "🌱" },
  { id: "laurent", name: "Laurent", role: "Winemaker", desc: "Implementation", color: "#228B22", emoji: "🛠️" },
  { id: "jeanpierre", name: "Jean-Pierre", role: "Grand Sommelier", desc: "Final Synthesis", color: "#722F37", emoji: "🎯" },
];

const scoringTiers = [
  { range: "95-100", name: "Legendary", icon: Trophy, color: "text-yellow-600", bg: "from-yellow-100 to-amber-100" },
  { range: "90-94", name: "Grand Cru", icon: Trophy, color: "text-amber-600", bg: "from-amber-100 to-yellow-100" },
  { range: "85-89", name: "Premier Cru", icon: Medal, color: "text-orange-600", bg: "from-orange-100 to-amber-100" },
  { range: "80-84", name: "Village", icon: Award, color: "text-green-600", bg: "from-green-100 to-emerald-100" },
  { range: "70-79", name: "Table Wine", icon: Star, color: "text-blue-600", bg: "from-blue-100 to-sky-100" },
  { range: "60-69", name: "House Wine", icon: Wine, color: "text-purple-600", bg: "from-purple-100 to-violet-100" },
  { range: "<60", name: "Corked", icon: AlertTriangle, color: "text-red-600", bg: "from-red-100 to-rose-100", span: true },
];

const features = [
  { icon: GitBranch, title: "Multi-Agent Analysis", desc: "6 specialized AI sommeliers evaluate your code in parallel" },
  { icon: Zap, title: "Real-time Streaming", desc: "Watch evaluations unfold live with SSE streaming" },
  { icon: FileText, title: "PDF Reports", desc: "Export professional tasting notes as shareable PDF" },
  { icon: Share2, title: "One-Click Share", desc: "Share results with your team instantly" },
];

const criteriaModes = [
  { name: "Basic", desc: "General code review", bestFor: "Everyday projects" },
  { name: "Hackathon", desc: "Gemini 3 judging criteria", bestFor: "Hackathon submissions" },
  { name: "Academic", desc: "Research-focused evaluation", bestFor: "Research projects" },
  { name: "Custom", desc: "Define your own criteria", bestFor: "Special requirements" },
];

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#FAF4E8] via-[#FDF8F0] to-[#F7E7CE]">
      {/* Hero Section */}
      <section className="relative px-6 pt-20 pb-16 overflow-hidden">
        <div className="max-w-6xl mx-auto">
          {/* Badge */}
          <div className="flex justify-center mb-8">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#722F37]/10 text-[#722F37] text-sm font-medium">
              <Sparkles className="w-4 h-4" />
              <span>Now with Gemini 3</span>
            </div>
          </div>

          {/* Main Title */}
          <div className="text-center mb-12">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-[#722F37] mb-6 shadow-xl shadow-[#722F37]/20">
              <Wine className="h-10 w-10 text-[#F7E7CE]" />
            </div>
            <h1 className="font-serif-elegant text-6xl md:text-7xl font-bold text-[#722F37] mb-4 tracking-tight">
              Somm
            </h1>
            <p className="text-2xl md:text-3xl font-light text-[#722F37]/80 mb-4">
              AI Code Evaluation
            </p>
            <p className="text-lg italic text-[#722F37]/60 max-w-2xl mx-auto">
              &ldquo;Every codebase has terroir. We&apos;re here to taste it.&rdquo;
            </p>
          </div>

          {/* Sommelier Avatars */}
          <div className="flex justify-center items-center gap-2 md:gap-4 mb-12 flex-wrap">
            {sommeliers.map((s, i) => (
              <div
                key={s.id}
                className="group relative"
                style={{ animationDelay: `${i * 100}ms` }}
              >
                <div className="w-16 h-16 md:w-20 md:h-20 rounded-full overflow-hidden border-3 border-white shadow-lg transition-transform duration-300 group-hover:scale-110 group-hover:-translate-y-1">
                  <Image
                    src={`/sommeliers/${s.id}.png`}
                    alt={s.name}
                    width={80}
                    height={80}
                    className="object-cover object-top w-full h-full"
                  />
                </div>
                {/* Tooltip */}
                <div className="absolute -bottom-8 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                  <span className="text-xs font-medium text-[#722F37] bg-white px-2 py-1 rounded shadow">
                    {s.name}
                  </span>
                </div>
              </div>
            ))}
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row justify-center items-center gap-4 mb-8">
            <Link
              href="/evaluate"
              className="inline-flex items-center gap-2 rounded-full bg-[#722F37] px-8 py-4 text-lg font-semibold text-[#F7E7CE] transition-all hover:bg-[#5A252C] hover:shadow-xl hover:shadow-[#722F37]/20"
            >
              Start Free Evaluation
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link
              href="/evaluate/demo/result"
              className="inline-flex items-center gap-2 rounded-full bg-white border-2 border-[#722F37]/20 px-8 py-4 text-lg font-semibold text-[#722F37] transition-all hover:border-[#722F37] hover:bg-[#722F37]/5"
            >
              See Demo Result
            </Link>
          </div>

          {/* Trust Badge */}
          <p className="text-center text-sm text-gray-500">
            Free for open source • No signup required
          </p>
        </div>

        {/* Scroll Indicator */}
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 animate-bounce">
          <ChevronDown className="w-6 h-6 text-[#722F37]/40" />
        </div>
      </section>

      {/* How It Works */}
      <section className="px-6 py-16 bg-white/50">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-serif-elegant font-bold text-[#722F37] text-center mb-4">
            How It Works
          </h2>
          <p className="text-center text-gray-600 mb-12 max-w-2xl mx-auto">
            Six specialized AI agents analyze your repository in parallel, then our Grand Sommelier synthesizes their findings into actionable insights.
          </p>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Step 1 */}
            <div className="text-center">
              <div className="w-16 h-16 rounded-2xl bg-[#722F37]/10 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-[#722F37]">1</span>
              </div>
              <h3 className="font-semibold text-[#722F37] mb-2">Connect Repository</h3>
              <p className="text-sm text-gray-600">Paste any GitHub URL or select from your repos</p>
            </div>

            {/* Step 2 */}
            <div className="text-center">
              <div className="w-16 h-16 rounded-2xl bg-[#722F37]/10 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-[#722F37]">2</span>
              </div>
              <h3 className="font-semibold text-[#722F37] mb-2">Parallel Analysis</h3>
              <p className="text-sm text-gray-600">6 sommeliers evaluate structure, quality, security, and innovation</p>
            </div>

            {/* Step 3 */}
            <div className="text-center">
              <div className="w-16 h-16 rounded-2xl bg-[#722F37]/10 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-[#722F37]">3</span>
              </div>
              <h3 className="font-semibold text-[#722F37] mb-2">Get Results</h3>
              <p className="text-sm text-gray-600">Receive detailed tasting notes with scores and recommendations</p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="px-6 py-16">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-serif-elegant font-bold text-[#722F37] text-center mb-12">
            Features
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((f) => (
              <div key={f.title} className="bg-white rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
                <div className="w-12 h-12 rounded-lg bg-[#722F37]/10 flex items-center justify-center mb-4">
                  <f.icon className="w-6 h-6 text-[#722F37]" />
                </div>
                <h3 className="font-semibold text-[#722F37] mb-2">{f.title}</h3>
                <p className="text-sm text-gray-600">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Evaluation Modes */}
      <section className="px-6 py-16 bg-white/50">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-serif-elegant font-bold text-[#722F37] text-center mb-4">
            Evaluation Modes
          </h2>
          <p className="text-center text-gray-600 mb-12">
            Choose the criteria that fits your needs
          </p>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            {criteriaModes.map((mode) => (
              <div key={mode.name} className="bg-white rounded-xl p-5 border border-[#722F37]/10 hover:border-[#722F37]/30 transition-colors">
                <h3 className="font-semibold text-[#722F37] mb-1">{mode.name}</h3>
                <p className="text-sm text-gray-600 mb-3">{mode.desc}</p>
                <span className="text-xs text-[#722F37]/60 bg-[#722F37]/5 px-2 py-1 rounded">
                  {mode.bestFor}
                </span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* The Six Sommeliers */}
      <section className="px-6 py-16">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-serif-elegant font-bold text-[#722F37] text-center mb-12">
            Meet Your Sommeliers
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sommeliers.map((s) => (
              <div
                key={s.id}
                className="bg-white rounded-xl overflow-hidden shadow-sm hover:shadow-lg transition-all group"
              >
                <div className="h-24 relative" style={{ backgroundColor: s.color }}>
                  <div className="absolute right-2 top-2 w-20 h-20 rounded-full overflow-hidden border-3 border-white shadow-md">
                    <Image
                      src={`/sommeliers/${s.id}.png`}
                      alt={s.name}
                      width={80}
                      height={80}
                      className="object-cover object-top w-full h-full"
                    />
                  </div>
                  <div className="absolute left-4 bottom-4">
                    <span className="text-3xl">{s.emoji}</span>
                  </div>
                </div>
                <div className="p-4">
                  <h3 className="font-semibold text-[#722F37] text-lg">{s.name}</h3>
                  <p className="text-sm font-medium" style={{ color: s.color }}>{s.role}</p>
                  <p className="text-sm text-gray-600 mt-1">{s.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Scoring System */}
      <section className="px-6 py-16 bg-white/50">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-serif-elegant font-bold text-[#722F37] text-center mb-4">
            Scoring System
          </h2>
          <p className="text-center text-gray-600 mb-10">
            From legendary cellars to house wines — every codebase has its place
          </p>
          <div className="grid gap-3 md:grid-cols-4">
            {scoringTiers.map((tier) => {
              const Icon = tier.icon;
              return (
                <div
                  key={tier.name}
                  className={`rounded-lg bg-gradient-to-br ${tier.bg} p-4 text-center ${tier.span ? 'md:col-span-2' : ''}`}
                >
                  <div className={`flex justify-center mb-2 ${tier.color}`}>
                    <Icon size={24} />
                  </div>
                  <div className={`font-bold ${tier.color}`}>{tier.range}</div>
                  <div className={`text-sm ${tier.color} opacity-80`}>{tier.name}</div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="px-6 py-20">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-4xl font-serif-elegant font-bold text-[#722F37] mb-4">
            Ready to taste your code?
          </h2>
          <p className="text-lg text-gray-600 mb-8">
            Join thousands of developers who trust Somm to evaluate their repositories.
          </p>
          <Link
            href="/evaluate"
            className="inline-flex items-center gap-2 rounded-full bg-[#722F37] px-10 py-5 text-xl font-semibold text-[#F7E7CE] transition-all hover:bg-[#5A252C] hover:shadow-xl hover:shadow-[#722F37]/20"
          >
            Start Your Evaluation
            <ArrowRight className="w-6 h-6" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-[#722F37]/10 py-8 text-center text-sm text-gray-500">
        <p>© 2025 Somm.dev — AI Code Sommelier</p>
        <p className="mt-2">Powered by Gemini 3</p>
      </footer>
    </div>
  );
}
