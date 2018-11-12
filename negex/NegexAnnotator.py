"""Negex Annotator."""
import csv

from Negex import NegTagger, sort_rules


def annotate():
    """Annotate with negex."""
    rfile = open(r'negex_triggers.txt')
    irules = sort_rules(rfile.readlines())
    reports = csv.reader(open(r'Annotations-1-120.txt', 'rb'), delimiter='\t')
    reports.next()
    report_num = 0
    correct_num = 0
    ofile = open(r'negex_output.txt', 'w')
    output = []
    outputfile = csv.writer(ofile, delimiter='\t')
    for report in reports:
        tagger = NegTagger(sentence=report[2], phrases=[
            report[1]], rules=irules, negP=False)
        report.append(tagger.getNegTaggedSentence())
        report.append(tagger.getNegationFlag())
        report = report + tagger.getScopes()
        report_num += 1
        if report[3].lower() == report[5]:
            correct_num += 1
        output.append(report)
    outputfile.writerow(
        ['Percentage correct:', float(correct_num) / float(report_num)])
    for row in output:
        if row:
            outputfile.writerow(row)
    ofile.close()


if __name__ == '__main__':
    annotate()
