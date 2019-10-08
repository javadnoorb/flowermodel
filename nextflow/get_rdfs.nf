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

clipfile = clipfiles.flatMap()

process count_frames{
    conda params.condaenv

    input:
        file clipfile
    output:
        set file("${clipfile}"), stdout into clipfile_and_framecount
    """
    #!/usr/bin/env bash
    flowermodel framecount --filename $clipfile
    """
}


mapseq = {x ->  vallist = []   // get tuples of frame number and video file name
                for (n in 0..<(x[1] as int)){
                    vallist.add([n, x[0]])
                }
              return vallist
          }



clipfile_and_framecount_seq = clipfile_and_framecount
                                 .map{mapseq(it)}
                                 .flatMap()
                                 .randomSample(50, 0)


process get_blobs{
    conda params.condaenv
    
    input:
        set framecount, file(clipfile) from clipfile_and_framecount_seq
    output:
        set val("${clipfile.baseName}"), file("${clipfile}"), file('*') into frameblobs
    """
    #!/usr/bin/env bash
   
    flowermodel blob --filename $clipfile --frame-index $framecount  --out-dir .
    """
}


frameblobs_grouped = frameblobs
                         .map{[it[0], [it[1], it[2]]]}
                         .groupTuple()



process combine_blobfiles{
    conda params.condaenv
    
    input:
        val item from frameblobs_grouped

    flowermodel blobsummary --filename $moviefile/$clip --infer-monocolor
}

/*
process get_file_list {
    conda params.condaenv

    output:
        file 'mov_metadata.txt' into mov_metadata

    """
    #!/usr/bin/env python
    import flowermodel.calculate_rdf as fmcal

    mov_metadata = fmcal.get_mov_metadata($params.data_path)
    mov_metadata.to_csv('mov_metadata.txt', index=False, sep='\t')
    """
}

mov_metadata
    .collectFile()
    .splitCsv(header:true, sep:'\t')
    .map{ row -> row.movfile}
    .set {movfile}


process get_rdfs {
    conda params.condaenv

    input:
        val movfile
  
    script:
    """
    #!/usr/bin/env python
    import flowermodel.calculate_rdf as fmcal
    import os
    
    rdfobj = fmcal.vidrdf($params.data_path, "$movfile", nbins=$params.nbins, shellwidth=$params.shellwidth)
    rdfobj.get_rdfs_for_all_colorpairs()
    """
}

*/