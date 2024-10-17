
import omni.kit.pipapi

# omni.kit.pipapi.install(package="requests",
#                         version="2.32.3",
#                         module="requests", # sometimes module is different from package name
#                         ignore_import_check=False,  # module is used for import check
#                         ignore_cache=False,
#                         use_online_index=True,
#                         surpress_output=False,
#                         extra_args=[])



# import omni.kit.pipapi

# omni.kit.pipapi.install(package="heavyai",

#                         module="heavyai", # sometimes module is different from package name
#                         ignore_import_check=False,  # module is used for import check
#                         ignore_cache=False,
#                         use_online_index=True,
#                         surpress_output=False,
#                         extra_args=[])

omni.kit.pipapi.install(package="paho-mqtt",

                        module="paho-mqtt", # sometimes module is different from package name
                        ignore_import_check=False,  # module is used for import check
                        ignore_cache=False,
                        use_online_index=True,
                        surpress_output=False,
                        extra_args=[])
