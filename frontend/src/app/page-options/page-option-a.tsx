import { Wine, Trophy, Medal, Award, Star, AlertTriangle, Sparkles, ArrowRight, Github, Zap, FileText, Share2, ChevronDown } from "lucide-react";
import Link from "next/link";
import Image from "next/image";

const sommeliers = [
  { id: "marcel", name: "Marcel", role: "Cellar Master", desc: "Structure & Metrics", color: "#8B7355" },
  { id: "isabella", name: "Isabella", role: "Wine Critic", desc: "Code Quality", color: "#C41E3A" },
  { id: "heinrich", name: "Heinrich", role: "Quality Inspector", desc: "Security & Testing", color: "#2F4F4F" },
  { id: "sofia", name: "Sofia", role: "Vineyard Scout", desc: "Innovation & Tech", color: "#DAA520" },
  { id: "laurent", name: "Laurent", role: "Winemaker", desc: "Implementation", color: "#228B22" },
  { id: "jeanpierre", name: "Jean-Pierre", role: "Grand Sommelier", desc: "Final Synthesis", color: "#4169E1" },
];

const criteriaModes = [
  { name: "Basic", desc: "General code review", bestFor: "Everyday projects", weight: "Balanced" },
  { name: "Hackathon", desc: "Gemini 3 judging criteria", bestFor: "Hackathon submissions", weight: "Tech 40%" },
  { name: "Academic", desc: "Research-focused evaluation", bestFor: "Research projects", weight: "Novelty" },
  { name: "Custom", desc: "Define your own criteria", bestFor: "Special requirements", weight: "Flexible" },
];

const scoringTiers = [
  { range: "95-100", name: "Legendary", icon: Trophy, color: "text-yellow-600", bg: "from-yellow-100/80 to-amber-100/80", border: "border-yellow-300" },
  { range: "90-94", name: "Grand Cru", icon: Trophy, color: "text-amber-600", bg: "from-amber-100/80 to-yellow-100/80", border: "border-amber-300" },
  { range: "85-89", name: "Premier Cru", icon: Medal, color: "text-orange-600", bg: "from-orange-100/80 to-amber-100/80", border: "border-orange-300" },
  { range: "80-84", name: "Village", icon: Award, color: "text-emerald-600", bg: "from-emerald-100/80 to-green-100/80", border: "border-emerald-300" },
  { range: "70-79", name: "Table Wine", icon: Star, color: "text-blue-600", bg: "from-blue-100/80 to-sky-100/80", border: "border-blue-300" },
  { range: "60-69", name: "House Wine", icon: Wine, color: "text-purple-600", bg: "from-purple-100/80 to-violet-100/80", border: "border-purple-300" },
  { range: "<60", name: "Corked", icon: AlertTriangle, color: "text-red-600", bg: "from-red-100/80 to-rose-100/80", border: "border-red-300" },
];

export default function Home() {
  return (
    <div className="min-h-screen bg-[#FAF4E8] overflow-x-hidden">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-[#FAF4E8]/80 backdrop-blur-md border-b border-[#722F37]/10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-[#722F37] flex items-center justify-center">
              <Wine className="w-4 h-4 text-[#F7E7CE]" />
            </div>
            <span className="font-serif-elegant text-xl font-bold text-[#722F37]">Somm</span>
          </div>
          <div className="hidden md:flex items-center gap-8 text-sm text-[#722F37]/70">
            <a href="#how-it-works" className="hover:text-[#722F37] transition-colors">How It Works</a>
            <a href="#features" className="hover:text-[#722F37] transition-colors">Features</a>
            <a href="#pricing" className="hover:text-[#722F37] transition-colors">Pricing</a>
          </div>
          <Link
            href="/evaluate"
            className="px-4 py-2 bg-[#722F37] text-[#F7E7CE] rounded-full text-sm font-medium hover:bg-[#5A252C] transition-colors"
          >
            Start Evaluation
          </Link>
        </div>
      </nav>

      {/* Hero Section - Editorial Layout */}
      <section className="relative min-h-screen pt-32 pb-20 px-6">
        {/* Background Elements */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-1/4 -left-20 w-96 h-96 bg-[#722F37]/5 rounded-full blur-3xl" />
          <div className="absolute bottom-1/4 -right-20 w-80 h-80 bg-[#DAA520]/10 rounded-full blur-3xl" />
        </div>

        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left Content */}
            <div className="relative z-10">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#722F37]/10 text-[#722F37] text-sm font-medium mb-6">
                <Sparkles className="w-4 h-4" />
                <span>Now with Gemini 3</span>
              </div>

              <h1 className="font-serif-elegant text-5xl md:text-6xl lg:text-7xl font-bold text-[#722F37] leading-[1.1] mb-6">
                AI Code
                <br />
                <span className="italic font-normal">Evaluation</span>
                <br />
                with Sommelier
                <br />
                Sophistication
              </h1>

              <p className="text-lg text-gray-600 mb-8 max-w-lg leading-relaxed">
                Six specialized AI agents analyze your repositories from every angle—
                structure, quality, security, and innovation.
              </p>

              <div className="flex flex-col sm:flex-row gap-4">
                <Link
                  href="/evaluate"
                  className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-[#722F37] text-[#F7E7CE] rounded-full font-semibold hover:bg-[#5A252C] transition-all hover:shadow-xl hover:shadow-[#722F37]/20"
                >
                  Start Free Evaluation
                  <ArrowRight className="w-5 h-5" />
                </Link>
                <Link
                  href="/evaluate/demo/result"
                  className="inline-flex items-center justify-center gap-2 px-8 py-4 border-2 border-[#722F37]/20 text-[#722F37] rounded-full font-semibold hover:border-[#722F37] hover:bg-[#722F37]/5 transition-all"
                >
                  See Demo Result
                </Link>
              </div>

              <p className="mt-6 text-sm text-gray-500">
                Free for open source • No signup required
              </p>
            </div>

            {/* Right Content - Sommelier Collage */}
            <div className="relative">
              <div className="relative h-[500px] md:h-[600px]">
                {/* Central Image - Jean-Pierre */}
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-48 md:w-56 md:h-56 rounded-full overflow-hidden border-4 border-white shadow-2xl z-20">
                  <Image
                    src="/sommeliers/jeanpierre.png"
                    alt="Jean-Pierre"
                    fill
                    className="object-cover object-top"
                    priority
                  />
                </div>

                {/* Surrounding Images */}
                <div className="absolute top-0 left-1/4 w-28 h-28 rounded-full overflow-hidden border-3 border-white shadow-xl">
                  <Image src="/sommeliers/marcel.png" alt="Marcel" fill className="object-cover object-top" />
                </div>

                <div className="absolute top-[15%] right-[10%] w-24 h-24 rounded-full overflow-hidden border-3 border-white shadow-xl">
                  <Image src="/sommeliers/isabella.png" alt="Isabella" fill className="object-cover object-top" />
                </div>

                <div className="absolute top-[40%] right-0 w-20 h-20 rounded-full overflow-hidden border-3 border-white shadow-lg">
                  <Image src="/sommeliers/sofia.png" alt="Sofia" fill className="object-cover object-top" />
                </div>

                <div className="absolute bottom-[20%] right-[15%] w-26 h-26 rounded-full overflow-hidden border-3 border-white shadow-xl">
                  <Image src="/sommeliers/laurent.png" alt="Laurent" fill className="object-cover object-top" />
                </div>

                <div className="absolute bottom-[10%] left-[20%] w-22 h-22 rounded-full overflow-hidden border-3 border-white shadow-xl">
                  <Image src="/sommeliers/heinrich.png" alt="Heinrich" fill className="object-cover object-top" />
                </div>

                {/* Decorative Elements */}
                <div className="absolute top-[30%] left-[5%] w-16 h-16 rounded-full bg-[#722F37]/10" />
                <div className="absolute bottom-[30%] right-[5%] w-12 h-12 rounded-full bg-[#DAA520]/20" />
              </div>
            </div>
          </div>
        </div>

        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
          <ChevronDown className="w-6 h-6 text-[#722F37]/40" />
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-24 px-6 bg-white/50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="font-serif-elegant text-4xl font-bold text-[#722F37] mb-4">
              How It Works
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Like a master sommelier orchestrates a tasting panel, our AI agents analyze your code in parallel, then synthesize their findings into actionable insights.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Step 1 */}
            <div className="relative">
              <div className="bg-white rounded-2xl p-8 shadow-sm border border-[#722F37]/10 h-full">
                <div className="w-12 h-12 rounded-xl bg-[#722F37] text-[#F7E7CE] flex items-center justify-center text-xl font-bold mb-6">
                  1
                </div>
                <h3 className="text-xl font-semibold text-[#722F37] mb-3">Submit Repository</h3>
                <p className="text-gray-600">
                  Connect your GitHub repository or paste any public repo URL. Choose from 4 evaluation modes.
                </p>
              </div>
            </div>

            {/* Step 2 */}
            <div className="relative">
              <div className="bg-white rounded-2xl p-8 shadow-sm border border-[#722F37]/10 h-full">
                <div className="w-12 h-12 rounded-xl bg-[#722F37] text-[#F7E7CE] flex items-center justify-center text-xl font-bold mb-6">
                  2
                </div>
                <h3 className="text-xl font-semibold text-[#722F37] mb-3">Parallel Analysis</h3>
                <p className="text-gray-600 mb-4">
                  Six specialized sommeliers evaluate simultaneously:
                </p>
                <div className="flex flex-wrap gap-2">
                  {sommeliers.slice(0, 5).map((s) => (
                    <span
                      key={s.id}
                      className="text-xs px-2 py-1 rounded-full"
                      style={{ backgroundColor: `${s.color}15`, color: s.color }}
                    >
                      {s.name}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Step 3 */}
            <div className="relative">
              <div className="bg-white rounded-2xl p-8 shadow-sm border border-[#722F37]/10 h-full">
                <div className="w-12 h-12 rounded-xl bg-[#722F37] text-[#F7E7CE] flex items-center justify-center text-xl font-bold mb-6">
                  3
                </div>
                <h3 className="text-xl font-semibold text-[#722F37] mb-3">Get Verdict</h3>
                <p className="text-gray-600">
                  Jean-Pierre synthesizes all findings into a final verdict with detailed tasting notes and recommendations.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="font-serif-elegant text-4xl font-bold text-[#722F37] mb-4">
              Features
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Everything you need for comprehensive code evaluation
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { icon: Zap, title: "Real-time Streaming", desc: "Watch evaluations unfold live with SSE streaming" },
              { icon: FileText, title: "PDF Reports", desc: "Export professional tasting notes as shareable PDF" },
              { icon: Share2, title: "One-Click Share", desc: "Share results with your team instantly" },
              { icon: Github, title: "GitHub Integration", desc: "Seamlessly connect your repositories" },
            ].map((feature) => (
              <div key={feature.title} className="bg-white rounded-xl p-6 shadow-sm border border-[#722F37]/5 hover:shadow-md transition-shadow">
                <div className="w-12 h-12 rounded-lg bg-[#722F37]/10 flex items-center justify-center mb-4">
                  <feature.icon className="w-6 h-6 text-[#722F37]" />
                </div>
                <h3 className="font-semibold text-[#722F37] mb-2">{feature.title}</h3>
                <p className="text-sm text-gray-600">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Evaluation Modes */}
      <section className="py-24 px-6 bg-white/50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="font-serif-elegant text-4xl font-bold text-[#722F37] mb-4">
              Evaluation Modes
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Choose the criteria that fits your project
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {criteriaModes.map((mode, idx) => (
              <div
                key={mode.name}
                className="bg-white rounded-xl p-6 shadow-sm border border-[#722F37]/10 hover:border-[#722F37]/30 transition-all group"
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold text-[#722F37] text-lg">{mode.name}</h3>
                  <span className="text-xs px-2 py-1 bg-[#722F37]/5 text-[#722F37] rounded-full">
                    {mode.weight}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-3">{mode.desc}</p>
                <p className="text-xs text-[#722F37]/60">Best for: {mode.bestFor}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Meet Your Sommeliers */}
      <section className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="font-serif-elegant text-4xl font-bold text-[#722F37] mb-4">
              Meet Your Sommeliers
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Six AI experts, each with a unique perspective on code quality
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sommeliers.map((s) => (
              <div
                key={s.id}
                className="bg-white rounded-xl overflow-hidden shadow-sm border border-[#722F37]/5 hover:shadow-lg transition-all group"
              >
                <div className="h-28 relative" style={{ backgroundColor: s.color }}>
                  <div className="absolute right-4 -bottom-8 w-20 h-20 rounded-full overflow-hidden border-4 border-white shadow-lg">
                    <Image
                      src={`/sommeliers/${s.id}.png`}
                      alt={s.name}
                      fill
                      className="object-cover object-top"
                    />
                  </div>
                </div>
                <div className="p-6 pt-10">
                  <h3 className="font-semibold text-[#722F37] text-lg">{s.name}</h3>
                  <p className="text-sm font-medium" style={{ color: s.color }}>{s.role}</p>
                  <p className="text-sm text-gray-600 mt-2">{s.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Scoring System */}
      <section className="py-24 px-6 bg-white/50">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="font-serif-elegant text-4xl font-bold text-[#722F37] mb-4">
              Scoring System
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              From legendary cellars to house wines — every codebase has its place
            </p>
          </div>

          <div className="space-y-3">
            {scoringTiers.map((tier) => {
              const Icon = tier.icon;
              return (
                <div
                  key={tier.name}
                  className={`flex items-center gap-4 p-4 rounded-xl bg-gradient-to-r ${tier.bg} border ${tier.border}`}
                >
                  <div className={`w-10 h-10 rounded-lg bg-white/80 flex items-center justify-center ${tier.color}`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <div className="flex-1">
                    <div className={`font-semibold ${tier.color}`}>{tier.name}</div>
                  </div>
                  <div className={"font-bold text-lg " + tier.color}>{tier.range}</div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <div className="bg-[#722F37] rounded-3xl p-12 md:p-16 text-[#F7E7CE]">
            <h2 className="font-serif-elegant text-4xl md:text-5xl font-bold mb-4">
              Ready to taste your code?
            </h2>
            <p className="text-lg opacity-80 mb-8 max-w-xl mx-auto">
              Join thousands of developers who trust Somm to evaluate their repositories.
            </p>
            <Link
              href="/evaluate"
              className="inline-flex items-center gap-2 px-10 py-5 bg-[#F7E7CE] text-[#722F37] rounded-full font-semibold text-lg hover:bg-white transition-all hover:shadow-xl"
            >
              Start Your Evaluation
              <ArrowRight className="w-6 h-6" />
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 border-t border-[#722F37]/10">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-[#722F37] flex items-center justify-center">
              <Wine className="w-4 h-4 text-[#F7E7CE]" />
            </div>
            <span className="font-serif-elegant text-lg font-bold text-[#722F37]">Somm</span>
          </div>

          <p className="text-sm text-gray-500">
            © 2025 Somm.dev — AI Code Sommelier
          </p>

          <div className="flex items-center gap-6 text-sm text-gray-500">
            <a href="#" className="hover:text-[#722F37] transition-colors">GitHub</a>
            <a href="#" className="hover:text-[#722F37] transition-colors">Twitter</a>
            <a href="#" className="hover:text-[#722F37] transition-colors">Discord</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
