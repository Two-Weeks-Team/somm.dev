'use client';

import React, { useEffect, useState, lazy, Suspense, useRef } from 'react';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import { api } from '../../../../lib/api';
import { EvaluationResult } from '../../../../types';
import { ArrowLeft, Share2, Download, Check, Copy } from 'lucide-react';
import { ResultTabs, useResultTab, ResultTabId } from '../../../../components/ResultTabs';
import { TastingNotesTab } from '../../../../components/TastingNotesTab';
import { GraphSkeleton } from '../../../../components/graph/GraphSkeleton';
// PDF export uses native print dialog

const Graph2DTab = lazy(() => import('../../../../components/Graph2DTab').then(m => ({ default: m.Graph2DTab })));
const Graph3DTab = lazy(() => import('../../../../components/Graph3DTab').then(m => ({ default: m.Graph3DTab })));

function TabLoadingFallback() {
  return (
    <div className="md:h-[600px] h-[400px]">
      <GraphSkeleton />
    </div>
  );
}

export default function ResultPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;
  
  const [result, setResult] = useState<EvaluationResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useResultTab('tasting');
  const [copied, setCopied] = useState(false);
  const [exporting, setExporting] = useState(false);
  const contentRef = useRef<HTMLDivElement>(null);

  const handleShare = async () => {
    const shareUrl = window.location.href;
    const shareData = {
      title: `Somm.dev - ${result?.repoUrl || 'Repository'} Evaluation`,
      text: `Check out this code evaluation: ${result?.totalScore}/100 - ${result?.repoUrl}`,
      url: shareUrl,
    };

    try {
      if (navigator.share && navigator.canShare(shareData)) {
        await navigator.share(shareData);
      } else {
        await navigator.clipboard.writeText(shareUrl);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }
    } catch (err) {
      // Fallback to clipboard
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleExportPDF = () => {
    if (!result) return;
    
    setExporting(true);
    
    const printWindow = window.open('', '_blank');
    if (!printWindow) {
      setExporting(false);
      return;
    }

    const repoName = result.repoUrl?.split('/').pop() || 'Repository';
    const getTier = (score: number) => {
      if (score >= 95) return { name: 'Legendary', color: '#FFD700' };
      if (score >= 90) return { name: 'Grand Cru', color: '#C9A227' };
      if (score >= 85) return { name: 'Premier Cru', color: '#CD7F32' };
      if (score >= 80) return { name: 'Village', color: '#2E7D32' };
      if (score >= 70) return { name: 'Table Wine', color: '#5D4E8C' };
      return { name: 'House Wine', color: '#757575' };
    };
    const tier = getTier(result.totalScore || 0);
    
    const sommelierColors: Record<string, string> = {
      'Marcel': '#8B7355',
      'Isabella': '#C41E3A', 
      'Heinrich': '#2F4F4F',
      'Sofia': '#DAA520',
      'Laurent': '#228B22',
    };
    
    const sommelierImages: Record<string, string> = {
      'Marcel': '/sommeliers/marcel.png',
      'Isabella': '/sommeliers/isabella.png',
      'Heinrich': '/sommeliers/heinrich.png',
      'Sofia': '/sommeliers/sofia.png',
      'Laurent': '/sommeliers/laurent.png',
    };
    
    const baseUrl = window.location.origin;
    
    printWindow.document.write(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>Somm.dev Report - ${repoName}</title>
        <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
        <style>
          :root {
            --wine: #722F37;
            --wine-dark: #5D262D;
            --wine-light: #F7E7CE;
            --gold: #C9A227;
            --text: #2D2D2D;
            --text-muted: #6B6B6B;
            --bg: #FAFAF8;
            --border: #E8E4E0;
          }
          
          * { margin: 0; padding: 0; box-sizing: border-box; }
          
          body { 
            font-family: 'Inter', system-ui, sans-serif; 
            color: var(--text); 
            background: white;
            line-height: 1.7; 
            font-size: 14px;
          }
          
          .page { max-width: 720px; margin: 0 auto; padding: 60px 50px; }
          
          /* Cover Header */
          .cover { text-align: center; padding: 50px 0 40px; border-bottom: 1px solid var(--border); margin-bottom: 50px; }
          .cover-brand { 
            display: inline-flex; align-items: center; gap: 8px;
            font-size: 12px; letter-spacing: 4px; color: var(--wine); 
            text-transform: uppercase; margin-bottom: 25px;
          }
          .cover-brand svg { width: 20px; height: 20px; }
          .cover h1 { 
            font-family: 'Cormorant Garamond', serif; 
            font-size: 42px; font-weight: 600; color: var(--text);
            margin-bottom: 8px; letter-spacing: -0.5px;
          }
          .cover .repo { 
            font-family: 'SF Mono', Monaco, monospace; 
            font-size: 13px; color: var(--text-muted);
            background: var(--bg); padding: 6px 14px; border-radius: 4px;
            display: inline-block; margin-top: 10px;
          }
          .cover .meta { font-size: 12px; color: var(--text-muted); margin-top: 20px; }
          
          /* Score Card */
          .score-card { 
            display: flex; align-items: center; gap: 40px;
            padding: 35px 40px; margin: 40px 0;
            background: linear-gradient(135deg, var(--wine) 0%, var(--wine-dark) 100%);
            border-radius: 16px; color: white;
          }
          .score-main { text-align: center; flex-shrink: 0; }
          .score-number { 
            font-family: 'Cormorant Garamond', serif;
            font-size: 80px; font-weight: 700; line-height: 1; 
          }
          .score-label { font-size: 13px; opacity: 0.7; margin-top: 4px; }
          .score-tier { 
            display: inline-block; margin-top: 12px;
            padding: 6px 16px; background: rgba(255,255,255,0.15);
            border-radius: 20px; font-size: 13px; font-weight: 500;
          }
          .score-breakdown { flex: 1; }
          .score-breakdown h3 { font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; opacity: 0.7; margin-bottom: 15px; }
          .score-bar { display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }
          .score-bar-name { font-size: 12px; width: 70px; opacity: 0.9; }
          .score-bar-track { flex: 1; height: 6px; background: rgba(255,255,255,0.2); border-radius: 3px; overflow: hidden; }
          .score-bar-fill { height: 100%; background: var(--wine-light); border-radius: 3px; }
          .score-bar-value { font-size: 12px; font-weight: 600; width: 30px; text-align: right; }
          
          /* Verdict */
          .verdict { margin: 45px 0; padding: 30px 35px; background: var(--bg); border-radius: 12px; position: relative; }
          .verdict::before { 
            content: '"'; position: absolute; top: 15px; left: 20px;
            font-family: 'Cormorant Garamond', serif; font-size: 60px; 
            color: var(--wine); opacity: 0.2; line-height: 1;
          }
          .verdict-label { 
            font-size: 10px; text-transform: uppercase; letter-spacing: 2px; 
            color: var(--wine); margin-bottom: 12px; font-weight: 600;
          }
          .verdict blockquote { 
            font-family: 'Cormorant Garamond', serif;
            font-size: 20px; font-style: italic; color: var(--text);
            line-height: 1.6; padding-left: 25px;
          }
          .verdict-author { 
            margin-top: 15px; padding-left: 25px;
            font-size: 12px; color: var(--text-muted);
          }
          
          /* Sommeliers */
          .section-title { 
            font-family: 'Cormorant Garamond', serif;
            font-size: 24px; font-weight: 600; color: var(--text);
            margin: 50px 0 30px; padding-bottom: 12px;
            border-bottom: 2px solid var(--wine);
          }
          
          .sommelier { 
            margin-bottom: 35px; padding: 25px 0;
            border-bottom: 1px solid var(--border);
            page-break-inside: avoid;
          }
          .sommelier:last-child { border-bottom: none; }
          
          .sommelier-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }
          .sommelier-info { display: flex; align-items: center; gap: 12px; }
          .sommelier-avatar { 
            width: 48px; height: 48px; border-radius: 50%; 
            object-fit: cover; object-position: top;
            border: 2px solid;
          }
          .sommelier-name { font-weight: 600; font-size: 16px; }
          .sommelier-role { font-size: 12px; color: var(--text-muted); }
          
          .sommelier-score-badge { 
            display: flex; align-items: center; gap: 8px;
            padding: 8px 14px; background: var(--bg); border-radius: 8px;
          }
          .sommelier-score-value { font-size: 22px; font-weight: 700; }
          .sommelier-score-max { font-size: 13px; color: var(--text-muted); }
          
          .sommelier-feedback { 
            font-size: 14px; color: var(--text); line-height: 1.75;
            margin-bottom: 16px; text-align: justify;
          }
          
          .techniques { margin-top: 16px; }
          .techniques-label { 
            font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px;
            color: var(--text-muted); margin-bottom: 10px; font-weight: 500;
          }
          .techniques-list { display: flex; flex-wrap: wrap; gap: 6px; }
          .technique-tag { 
            font-size: 11px; padding: 5px 12px; 
            background: white; border: 1px solid var(--border);
            border-radius: 15px; color: var(--text-muted);
          }
          
          /* Footer */
          .footer { 
            margin-top: 60px; padding-top: 25px; 
            border-top: 1px solid var(--border);
            display: flex; justify-content: space-between; align-items: center;
          }
          .footer-brand { font-size: 12px; color: var(--wine); font-weight: 500; }
          .footer-meta { font-size: 11px; color: var(--text-muted); }
          
          @media print { 
            .page { padding: 40px 35px; }
            .sommelier { page-break-inside: avoid; }
          }
        </style>
      </head>
      <body>
        <div class="page">
          <div class="cover">
            <div class="cover-brand">
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C10.08 2 8.5 3.58 8.5 5.5c0 1.58 1.07 2.9 2.5 3.33V19h-3v2h8v-2h-3V8.83c1.43-.43 2.5-1.75 2.5-3.33C15.5 3.58 13.92 2 12 2zm0 5c-.83 0-1.5-.67-1.5-1.5S11.17 4 12 4s1.5.67 1.5 1.5S12.83 7 12 7z"/></svg>
              Somm.dev
            </div>
            <h1>Code Evaluation Report</h1>
            <div class="repo">${result.repoUrl || 'Repository'}</div>
            <div class="meta">${new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</div>
          </div>
          
          <div class="score-card">
            <div class="score-main">
              <div class="score-number">${result.totalScore}</div>
              <div class="score-label">out of 100</div>
              <div class="score-tier" style="background: ${tier.color}33; color: ${tier.color}">${tier.name}</div>
            </div>
            <div class="score-breakdown">
              <h3>Score Breakdown</h3>
              ${result.results.map(s => `
                <div class="score-bar">
                  <span class="score-bar-name">${s.name}</span>
                  <div class="score-bar-track"><div class="score-bar-fill" style="width: ${s.score}%"></div></div>
                  <span class="score-bar-value">${s.score}</span>
                </div>
              `).join('')}
            </div>
          </div>
          
          <div class="verdict">
            <div class="verdict-label">Executive Summary</div>
            <blockquote>${result.finalVerdict}</blockquote>
            <div class="verdict-author">— Jean-Pierre, Grand Sommelier</div>
          </div>
          
          <h2 class="section-title">Detailed Evaluations</h2>
          
          ${result.results.map(s => {
            const color = sommelierColors[s.name] || '#722F37';
            return `
            <div class="sommelier">
              <div class="sommelier-header">
                <div class="sommelier-info">
                  <img class="sommelier-avatar" src="${baseUrl}${sommelierImages[s.name] || '/sommeliers/jeanpierre.png'}" style="border-color: ${color}" alt="${s.name}">
                  <div>
                    <div class="sommelier-name">${s.name}</div>
                    <div class="sommelier-role">${s.role || 'Sommelier'}</div>
                  </div>
                </div>
                <div class="sommelier-score-badge">
                  <span class="sommelier-score-value" style="color: ${color}">${s.score}</span>
                  <span class="sommelier-score-max">/ 100</span>
                </div>
              </div>
              <div class="sommelier-feedback">${s.feedback}</div>
              ${s.recommendations && s.recommendations.length > 0 ? `
                <div class="techniques">
                  <div class="techniques-label">Techniques Applied</div>
                  <div class="techniques-list">
                    ${s.recommendations.map(r => `<span class="technique-tag">${r}</span>`).join('')}
                  </div>
                </div>
              ` : ''}
            </div>
          `}).join('')}
          
          <div class="footer">
            <div class="footer-brand">Somm.dev — AI-Powered Code Evaluation</div>
            <div class="footer-meta">Powered by Gemini</div>
          </div>
        </div>
      </body>
      </html>
    `);
    
    printWindow.document.close();
    printWindow.onload = () => {
      printWindow.print();
      setExporting(false);
    };
  };

  useEffect(() => {
    const fetchResult = async () => {
      try {
        const data = await api.getEvaluationResult(id);
        setResult(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load results');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchResult();
    }
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#FAFAFA]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#722F37] mx-auto mb-4"></div>
          <p className="text-[#722F37] font-medium">Decanting results...</p>
        </div>
      </div>
    );
  }

  if (error || !result) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#FAFAFA]">
        <div className="text-center max-w-md mx-auto p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Corked!</h2>
          <p className="text-gray-600 mb-6">{error || 'Result not found'}</p>
          <button
            onClick={() => router.push('/evaluate')}
            className="px-6 py-2 bg-[#722F37] text-white rounded-lg hover:bg-[#5a252c] transition-colors"
          >
            Try Another Vintage
          </button>
        </div>
      </div>
    );
  }

  const renderTabContent = (tabId: ResultTabId) => {
    switch (tabId) {
      case 'tasting':
        return <TastingNotesTab result={result} />;
      case 'graph-2d':
        return (
          <Suspense fallback={<TabLoadingFallback />}>
            <Graph2DTab evaluationId={id} />
          </Suspense>
        );
      case 'graph-3d':
        return (
          <Suspense fallback={<TabLoadingFallback />}>
            <Graph3DTab evaluationId={id} />
          </Suspense>
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-[#FAFAFA]">
      <div className="max-w-5xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center mb-6">
          <button
            onClick={() => router.push('/evaluate')}
            className="flex items-center text-gray-600 hover:text-[#722F37] transition-colors"
          >
            <ArrowLeft size={20} className="mr-2" />
            New Tasting
          </button>
          <div className="flex space-x-4">
            <button 
              onClick={handleShare}
              className="flex items-center px-4 py-2 text-sm font-medium text-[#722F37] bg-white border border-[#722F37] rounded-lg hover:bg-[#FAFAFA] transition-colors"
            >
              {copied ? <Check size={16} className="mr-2" /> : <Share2 size={16} className="mr-2" />}
              {copied ? 'Copied!' : 'Share'}
            </button>
            <button 
              onClick={handleExportPDF}
              disabled={exporting}
              className="flex items-center px-4 py-2 text-sm font-medium text-white bg-[#722F37] rounded-lg hover:bg-[#5a252c] transition-colors disabled:opacity-50"
            >
              <Download size={16} className={`mr-2 ${exporting ? 'animate-pulse' : ''}`} />
              {exporting ? 'Exporting...' : 'Export PDF'}
            </button>
          </div>
        </div>

        <ResultTabs activeTab={activeTab} onTabChange={setActiveTab} />

        <div ref={contentRef}>
          {renderTabContent(activeTab)}
        </div>
      </div>
    </div>
  );
}
