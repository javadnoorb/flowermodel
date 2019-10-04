#!/usr/bin/env nextflow

movfiles = Channel.fromPath(params.moviespath+'/41586_2019_1429_MOESM3_ESM.mov')

process clip_files_if_needed{
    conda params.condaenv

    input:
        file 'movfile.mov' from movfiles
    output:
        file '*.mov' into clipfiles
    """
    #!/usr/bin/env bash
    flowermodel clip --filename movfile.mov --infer-dimensions
    """
}

clipfiles
    .flatMap()
    .subscribe{ println "${it}" }

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