import 'package:bloc/bloc.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:syncademic_app/models/sync_profile.dart';

part 'sync_profile_2_state.dart';
part 'sync_profile_2_cubit.freezed.dart';

class SyncProfile_2Cubit extends Cubit<SyncProfile_2State> {
  SyncProfile_2Cubit() : super(SyncProfile_2State.initial());
}
