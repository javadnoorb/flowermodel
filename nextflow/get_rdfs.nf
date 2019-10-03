#!/usr/bin/env nextflow

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

