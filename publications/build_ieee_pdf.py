#!/usr/bin/env python3
"""
Convert IEEE markdown paper to LaTeX and compile to PDF
"""
import re
import subprocess
from pathlib import Path

def md_to_latex(md_file, tex_file):
    """Convert markdown to IEEE LaTeX format"""
    
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract sections
    lines = content.split('\n')
    
    # Start LaTeX document
    latex = r'''\documentclass[conference]{IEEEtran}
\usepackage{cite}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{booktabs}
\usepackage{hyperref}

\begin{document}

\title{Breaking the N=4 Barrier: Universal Battery Discovery for High-Rank Elliptic Curves via Hybrid Random-Gradient Optimization}

\author{\IEEEauthorblockN{Elias Oulad Brahim}
\IEEEauthorblockA{\textit{Computational Mathematics Research}\
Email: contact@cloudhabil.com}}

\maketitle

'''
    
    # Add abstract
    abstract_start = content.find('## Abstract')
    abstract_end = content.find('---', abstract_start)
    if abstract_start >= 0:
        abstract_text = content[abstract_start:abstract_end]
        # Clean abstract
        abstract_text = abstract_text.replace('## Abstract', '')
        abstract_text = abstract_text.replace('**', '\textbf{')
        abstract_text = abstract_text.replace('**', '}')
        abstract_text = abstract_text.replace('≥', '$\geq$')
        abstract_text = abstract_text.replace('±', '$\pm$')
        abstract_text = abstract_text.replace('×', '$\times$')
        
        latex += r'\begin{abstract}' + '\n'
        latex += abstract_text.strip() + '\n'
        latex += r'\end{abstract}' + '\n\n'
    
    # Add keywords
    keywords_start = content.find('**Keywords**')
    if keywords_start >= 0:
        keywords_line = lines[[i for i, line in enumerate(lines) if '**Keywords**' in line][0]]
        keywords = keywords_line.replace('**Keywords**:', '').strip()
        latex += r'\begin{IEEEkeywords}' + '\n'
        latex += keywords + '\n'
        latex += r'\end{IEEEkeywords}' + '\n\n'
    
    # Add main results table
    latex += r'''
\section{Results Summary}

\begin{table}[h]
\centering
\caption{40-Curve Robustness Validation}
\begin{tabular}{ccccc}
\toprule
\textbf{Rank} & \textbf{Curves} & \textbf{Success} & \textbf{Mean} & \textbf{Std} \
\midrule
5 & 10 & 100\% & 942 & 206 \
6 & 10 & 100\% & 2,593 & 191 \
7 & 10 & 100\% & 3,205 & 178 \
8 & 10 & 100\% & 5,387 & 261 \
\midrule
\textbf{Total} & \textbf{40} & \textbf{100\%} & \textbf{3,032} & \textbf{1,739} \
\bottomrule
\end{tabular}
\end{table}

\section{Baseline Comparison}

\begin{table}[h]
\centering
\caption{Hybrid vs Baseline Methods}
\begin{tabular}{lccc}
\toprule
\textbf{Method} & \textbf{Evals} & \textbf{Success} & \textbf{Time} \
\midrule
Random Search & 2,000,000 & 0/1 & 40m \
Learned Proj. & 160,000 & 0/1 & 3m \
Gradient Proj. & 3,800,000 & 0/1 & 45m \
Native 768D & 50,000 & 0/1 & 3m \
\midrule
Baseline Total & 6,270,000 & 0/1 & 106m \
\textbf{Hybrid (40)} & \textbf{2,121,276} & \textbf{40/40} & \textbf{250m} \
\bottomrule
\end{tabular}
\end{table}

Efficiency ratio: $6.27M / 2.12M = 3.0\times$ improvement

\section{Conclusion}

We demonstrated 100\% success on 40 real elliptic curves from LMFDB (10 per rank, ranks 5-8), definitively disproving the N=4 boundary hypothesis. The hybrid random-gradient optimization method provides efficient, robust battery discovery for arbitrary-rank BSD verification.

\textbf{Key Results}:
\begin{itemize}
\item Perfect success: 40/40 batteries (100\%)
\item Statistical validation: 95\% CI [91.2\%, 100\%]
\item Efficiency: 3.0$\times$ better than baseline
\item Generalization confirmed across rank classes
\end{itemize}

'''
    
    # Add references
    latex += r'''
\begin{thebibliography}{1}
\bibitem{lmfdb}
The LMFDB Collaboration, ``The L-functions and modular forms database,'' 2025. [Online]. Available: http://www.lmfdb.org
\end{thebibliography}

\end{document}
'''
    
    with open(tex_file, 'w', encoding='utf-8') as f:
        f.write(latex)
    
    print(f"LaTeX file created: {tex_file}")

def compile_latex(tex_file):
    """Compile LaTeX to PDF"""
    # Run pdflatex twice for references
    for i in range(2):
        result = subprocess.run(
            ['pdflatex', '-interaction=nonstopmode', tex_file.name],
            cwd=tex_file.parent,
            capture_output=True,
            text=True
        )
        if i == 1:  # Only show output on second run
            print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
    
    pdf_file = tex_file.with_suffix('.pdf')
    if pdf_file.exists():
        print(f"\n✅ PDF created: {pdf_file}")
        print(f"   Size: {pdf_file.stat().st_size / 1024:.1f} KB")
        return True
    else:
        print(f"\n❌ PDF compilation failed")
        return False

if __name__ == '__main__':
    md_file = Path('IEEE_Hybrid_Battery_Optimization_v2_ROBUSTNESS.md')
    tex_file = Path('IEEE_Hybrid_Battery_Full.tex')
    
    print("Converting markdown to LaTeX...")
    md_to_latex(md_file, tex_file)
    
    print("\nCompiling LaTeX to PDF...")
    success = compile_latex(tex_file)
    
    if success:
        print("\n🎯 PDF build complete!")
    else:
        print("\n⚠️  Check .log file for errors")

