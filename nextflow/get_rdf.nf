#!/usr/bin/env nextflow

movfile = Channel.fromPath(params.moviespath+'/*.mov')

process clip_files_if_needed{
    conda params.condaenv

    input:
        file movfile
    output:
        file '*.mov' into clipfiles
    """
    #!/usr/bin/env bash
    flowermodel clip --filename $movfile --infer-dimensions
    """
}


clipfiles
    .flatMap()
    .map{[it.getName(), it]}
    .into{clipfile1; clipfile2}


process count_frames{
    conda params.condaenv

    input:
        set val(clip_id), file(clipfile) from clipfile1
    output:
        set val("${clip_id}"), file("${clipfile}"), stdout into clipfile_and_framecount
    """
    #!/usr/bin/env bash
    flowermodel framecount --filename $clipfile
    """
}


mapseq = {x ->  vallist = []   // get tuples of frame number and video file name
                for (n in 0..<(x[2] as int)){
                    vallist.add([x[0], n, x[1]])
                }
              return vallist
          }


clipfile_and_framecount
             .map{mapseq(it)}
             .flatMap()
             .into{clipfile_and_framecount_seq; clipfile_and_framecount_seq2}

process get_blobs{
    conda params.condaenv
    
    input:
        set val(clip_id), val(framecount), file(clipfile) from clipfile_and_framecount_seq
    output:
        set val("${clip_id}"), file('*') into frameblobs
    """
    #!/usr/bin/env bash
   
    flowermodel blob --filename $clipfile --frame-index $framecount  --out-dir .
    """
}

frameblobs_grouped = frameblobs
                         .groupTuple()
                         .map{[it[0], it[1].join(" ")]}


process combine_blobfiles{
    conda params.condaenv

    input:
        val item from frameblobs_grouped
    output:
        set val("${item[0]}"), file("*.blobs.csv") into blobsfile
    """
    #!/usr/bin/env bash
    
    flowermodel blobsummary --filenames ${item[1]} --infer-monocolor --output-file ${item[0]}.blobs.csv
    """
}


blobsfile_and_clipfiles = blobsfile.join(clipfile2) // join the two based on clip id

process get_rdfs {
    publishDir rdffiles, mode: 'link', overwrite: true
    conda params.condaenv

    input:
        set val(clip_id), file(blobsfile), file(clipfile) from blobsfile_and_clipfiles
    output:
        set val("${clip_id}"), file('*.csv') into rdffiles
    
    script:
    """
    #!/usr/bin/env python
    import flowermodel.calculate_rdf as fmcal
    import os

    rdfobj = fmcal.vidrdf("$blobsfile", "$clipfile", nbins=$params.nbins, shellwidth=$params.shellwidth)
    rdfobj.get_rdfs_for_all_colorpairs()
    """
}


rdffiles.view()