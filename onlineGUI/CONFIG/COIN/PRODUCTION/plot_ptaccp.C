/*
  Script to plot Pt acceptance with necessary canvas customizations
*/

void PlotPtAccHisto(TH2* h2);

void plot_ptaccp() {
  TH2F *h2ptaccp = (TH2F*)gDirectory->Get("h2ptaccp");
  if (!h2ptaccp) {
    std::cerr << "ERROR: Histogram 'h2ptaccp' not found in gDirectory!" << std::endl;
    return;  // or throw, or exit, or handle appropriately
  }
  PlotPtAccHisto(h2ptaccp);
}

//----------------------------------------------------------
void PlotPtAccHisto(TH2* h2) {
  /* Special function to plot P_T acceptance histo */
  h2->SetStats(0);
  h2->GetXaxis()->SetRangeUser(-1, 1);
  h2->GetYaxis()->SetRangeUser(-1, 1);
  h2->GetXaxis()->SetLabelSize(0);  // hide default tick labels
  h2->GetYaxis()->SetLabelSize(0);
  h2->Draw("COL");
  
  // Draw vertical and horizontal lines
  TLine *lx = new TLine(-1, 0, 1, 0);
  TLine *ly = new TLine(0, -1, 0, 1);
  lx->SetLineColor(kGray+2); ly->SetLineColor(kGray+2);
  lx->Draw(); ly->Draw();

  // Draw circular guides and labels
  TLatex* label = new TLatex();
  label->SetTextSize(0.025);  // small, unobtrusive
  label->SetTextColor(kRed);
  label->SetTextAlign(12);    // left-bottom alignment

  for (double r : {0.2, 0.4, 0.6, 0.8}) {
    TEllipse *circle = new TEllipse(0, 0, r);
    circle->SetFillStyle(0);
    circle->SetLineStyle(2);
    circle->SetLineColor(kGray+2);
    circle->Draw();

    // Label each circle near the top-right quadrant
    double x = r / sqrt(2), y = r / sqrt(2);
    label->DrawLatex(x + 0.02, y + 0.02, Form("p_{T} = %.1f", r));
  }

  // Draw angular labels
  TLatex* t = new TLatex();
  t->SetTextAlign(22);
  t->SetTextSize(0.035);
  t->DrawLatex(1.1, 0, "#phi_{h}=0#circ");
  t->DrawLatex(0, 1.08, "#phi_{h}=90#circ");
  t->DrawLatex(-1.12, 0, "#phi_{h}=180#circ");
  t->DrawLatex(0, -1.08, "#phi_{h}=270#circ");
}
