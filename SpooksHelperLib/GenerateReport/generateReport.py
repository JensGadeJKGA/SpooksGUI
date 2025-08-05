import os
import numpy as np
import pandas
import contextlib
import PyPDF2
from shutil import copyfile

from SpooksHelperLib.Utils import utils
from SpooksHelperLib.GenerateReport.generatePDF import generatePDF
from SpooksHelperLib.GenerateReport.reportFront import reportFront
from SpooksHelperLib.Vequilibrium import verticalEquilibrium
from SpooksHelperLib.Steel_Sheet_Pile_Wall import steel_sheet_pile_implementer


class generateReport:
    def __init__(self):
        pass

    def ReportGenerator(self,GetResultsOutput,OutputDirList,Version):
        print('Generating report...')

        ## Vertical equilibrium
        
        VerticalEquilibriumOutput = verticalEquilibrium.VerticalEquilibrium(GetResultsOutput)    

        if GetResultsOutput['Analysis']['SheetPileAddOnInput']['UseAddOn'] == 'Yes':
        # try:
            SheetPileAddOnResults = steel_sheet_pile_implementer(GetResultsOutput)
            #except Exception as E:
            #    print(f"Error processing sheet pile results: {E}")  # Debugging output
                
            #    SheetPileAddOnResults = {'SheetPileProfile': 'N/A',
            #                             'RUR': 'N/A',
            #                             'RURLevel': 'N/A',
            #                             'RotCap': 'N/A'}
                
        else:
            
            SheetPileAddOnResults = {'SheetPileProfile': 'N/A',
                                    'RUR': 'N/A',
                                    'RURLevel': 'N/A',
                                    'RotCap': 'N/A'}
        
        TempReportFrontPath = reportFront.ReportFront(VerticalEquilibriumOutput,OutputDirList,Version)
        TemporaryPathResults = generatePDF.PDFGenerator(VerticalEquilibriumOutput, SheetPileAddOnResults, Version)
        
        ## Temporary file dir
        TemporaryPathReport = utils.TemporaryWorkingDirectory()
        
        ## Temporary report file dir
        TemporaryPathReport = os.path.join(TemporaryPathReport, r'Report.pdf')
                    
        
        ### pdfs to merge (existing file, plot, results)               
        pdfsToMerge = [TempReportFrontPath, TemporaryPathResults]
        
        
        ## Merging pdfs
        with contextlib.ExitStack() as stack:
            try:
                pdfMerger = PyPDF2.PdfMerger()
            except AttributeError:
                pdfMerger = PyPDF2.PdfFileMerger()
            files = [stack.enter_context(open(pdf, 'rb')) for pdf in pdfsToMerge]
            for f in files:
                pdfMerger.append(f)
            with open(TemporaryPathReport, 'wb') as f:
                pdfMerger.write(f)
                
            f.close()
        
        ### Deleting input pdfs
        os.remove(TempReportFrontPath)
        os.remove(TemporaryPathResults)

        return TemporaryPathReport
        
        
        
    def ReportsMerger(self,FeederOutput,OutputDirList,Version,stat,tabcalc,pb,calcno):
        
        stat.configure(text = "Generating reports...")
        ## Progress bar maximum
        pb['maximum'] = len(FeederOutput)-1
        pb.update() ## update progress bar
        tabcalc.update_idletasks()
        
        print('Merging report pages...')

        
            
        
        ## Temporary file dir
        TemporaryDir = utils.TemporaryWorkingDirectory()
        
        OutputDirectory = os.path.join(OutputDirList[-1],r'WinSpooksReport.pdf')
        
        ## Inital empty file
        TempFile = os.path.join(TemporaryDir, r'TempFile.pdf')
        TemporaryFile = os.path.join(TemporaryDir, r'WinSpooksReport.pdf')
        
        
        Initial = None
        
        ## Loop through all calculated analyses
        for AnalysisOutput in FeederOutput:
            
            ### PROGRESS BAR AND CALCULATION NO UPDATE
            AnalysisNo = AnalysisOutput.get('ExecuteOutput').get('Analysis').get('AnalysisNo')
            calcno.configure(text = str(AnalysisNo)) ## Calculation number for GUI
            tabcalc.update_idletasks()
            pb['value'] = AnalysisNo
            pb.update() ## update progress bar
            
            
            GetResultsOutput = AnalysisOutput.get('GetResultsOutput')
            
            
            ## Generate report including vertical equilibrium
            
            TemporaryPathReport = self.ReportGenerator(GetResultsOutput,OutputDirList,Version)
            
            
            if Initial == None:
                
                ## If old report exists -> remove
                try:
                    os.remove(TemporaryFile)
                    
                except:
                    pass
                
                os.rename(TemporaryPathReport,TemporaryFile)
            
            else:
            
                ## Get analysis report (.pdf)
                pdfsToMerge = [TemporaryFile, TemporaryPathReport]
            
                ## Append to initial .pdf file
                ## Merging pdfs
                with contextlib.ExitStack() as stack:
                    try:
                        pdfMerger = PyPDF2.PdfMerger()
                    except AttributeError:
                        pdfMerger = PyPDF2.PdfFileMerger()
                    files = [stack.enter_context(open(pdf, 'rb')) for pdf in pdfsToMerge]
                    for f in files:
                        pdfMerger.append(f)
                
                    with open(TempFile, 'wb') as f:
                        pdfMerger.write(f)
                            
                        f.close()
                
                try:
                    os.remove(TemporaryFile)
                except:
                    pass
                    
            
                os.rename(TempFile,TemporaryFile)
                
            Initial = 1
                
                    
        ## Copy report to user defined destination


        try:
            copyfile(TemporaryFile,OutputDirectory)
        except:
            copyfile(TemporaryPathReport,OutputDirectory)