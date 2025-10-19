import React from "react";
import { Brain, Menu, X } from "lucide-react";
import { Button } from "./ui/Button";

export default function Layout({ children }) {
  const [sidebarOpen, setSidebarOpen] = React.useState(false);

  return (
    <div 
      className="min-h-screen relative overflow-hidden"
      style={{
        background: "linear-gradient(135deg, #0f2027 0%, #203a43 25%, #2c5364 50%, #1a2a6c 75%, #0f1642 100%)",
      }}
    >
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-0 w-96 h-96 bg-blue-600/20 rounded-full blur-3xl animate-pulse" 
          style={{ animation: "pulse 4s ease-in-out infinite" }} />
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-indigo-600/20 rounded-full blur-3xl animate-pulse" 
          style={{ animation: "pulse 6s ease-in-out infinite", animationDelay: "2s" }} />
        <div className="absolute top-1/2 left-1/2 w-96 h-96 bg-cyan-600/15 rounded-full blur-3xl animate-pulse" 
          style={{ animation: "pulse 8s ease-in-out infinite", animationDelay: "4s" }} />
      </div>

      {/* Mobile menu button */}
      <div className="lg:hidden fixed top-4 left-4 z-50">
        <Button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="backdrop-blur-xl bg-white/10 border border-white/20 hover:bg-white/20"
          size="icon"
        >
          {sidebarOpen ? (
            <X className="w-5 h-5 text-white" />
          ) : (
            <Menu className="w-5 h-5 text-white" />
          )}
        </Button>
      </div>

      {/* Header */}
      <div className="relative z-10 backdrop-blur-xl bg-white/10 border-b border-white/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-center lg:justify-start gap-3">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center backdrop-blur-xl border border-white/20"
              style={{
                boxShadow: "0 0 30px rgba(59, 130, 246, 0.5)",
              }}
            >
              <Brain className="w-7 h-7 text-white" />
            </div>
            <div className="text-center lg:text-left">
              <h1 className="text-2xl font-bold text-white">AI Network Brain</h1>
              <p className="text-sm text-blue-200">Intelligent network analysis powered by RAG + AI</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="relative z-10">
        {children}
      </div>

      {/* Footer */}
      <div className="relative z-10 backdrop-blur-xl bg-white/10 border-t border-white/20 mt-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-center text-sm text-blue-200">
            <div>
              <span className="font-semibold text-white">AI Brain:</span> RAG + distilgpt2
            </div>
            <div>
              <span className="font-semibold text-white">Analysis:</span> Real-time CLI
            </div>
            <div>
              <span className="font-semibold text-white">Version:</span> 8.0.0
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

