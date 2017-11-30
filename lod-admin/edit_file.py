

with open("../data/lod_files/ArchivesHubLinkedDataDump_04-03-2014.nt", "rt") as fin:
    with open("../data/lod_files/ArchivesHubLinkedDataDump_04-03-2014_.nt", "wt") as fout:
        for line in fin:
            fout.write(line.replace('@EN', ''))

